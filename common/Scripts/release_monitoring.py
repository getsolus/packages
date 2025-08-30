#!/usr/bin/python3
from dataclasses import asdict, dataclass
import os
from pathlib import Path
import re
from sys import argv
from typing import List, Optional, Union
from urllib3.util import parse_url, Url
import yaml
import requests
from datetime import datetime


def represent_none(self, _):
    return self.represent_scalar("tag:yaml.org,2002:null", "~")


yaml.add_representer(type(None), represent_none)


@dataclass
class Releases:
    id: Optional[int]
    rss: Optional[str]


@dataclass
class Cpe:
    vendor: Optional[str]
    product: Optional[str]


@dataclass
class Security:
    cpe: Optional[List[Cpe]]


@dataclass
class YamlData:
    releases: Releases
    security: Security


class ReleaseMonitoring:
    def __init__(
        self,
        release: YamlData,
        homepage: Optional[str] = None,
        name: Optional[str] = None,
        latest_version: Optional[str] = None,
    ):
        self._homepage = homepage
        self._name = name
        self._release = release
        self._latest_version = latest_version

    @property
    def homepage(self):
        return self._homepage

    @property
    def name(self):
        return self._name

    @property
    def latest_version(self):
        return self._latest_version

    def to_yaml(self, filename: str):
        lines = yaml.dump(
            asdict(self._release), default_flow_style=False, sort_keys=False
        ).splitlines()

        if self._release.releases.id is None:
            pattern = "?pattern=" + self.name if self.name else ""
            lines[
                1
            ] += f" # Check https://release-monitoring.org/projects/search/{pattern}"

        if self._release.releases.rss is None:
            lines[2] += " # For example https://github.com/PyO3/maturin/releases.atom"

        if self._release.security.cpe is None:
            lines.insert(3, f" # No known CPE, checked {datetime.now():%Y-%m-%d}")
        else:
            lines.insert(
                3,
                "# Verify successful cpe hits by visiting https://cve.circl.lu/search?vendor=$VENDOR&product=$PRODUCT",
            )

        with open(filename, "w") as f:
            f.write("\n".join(lines) + "\n")


def check_cpe(search_pattern: str) -> Optional[List[dict]]:
    """
    Check if a CPE (Common Platform Enumeration) exists for the package.
    Returns (found, cpe_data) where cpe_data can be a list of dicts or None.
    """
    try:
        response = requests.post(
            "https://cpe-guesser.cve-search.org/search",
            json={"query": [search_pattern]},
            timeout=10,
        )
        response.raise_for_status()
        cpe_data = response.json()

        if cpe_data and len(cpe_data) >= 1:
            cpe_entries = []
            for cpe_entry in cpe_data[:5]:
                if isinstance(cpe_entry, list) and len(cpe_entry) >= 2:
                    cpe_string = cpe_entry[1]

                    parts = cpe_string.split(":")
                    if len(parts) >= 5:
                        vendor = parts[3]
                        product = parts[4]
                        cpe_entries.append({"vendor": vendor, "product": product})

            if cpe_entries:
                return cpe_entries

        return None

    except Exception as e:
        print(f"CPE check error: {e}")
        return None


def get_known_rss_url(
    package_name: str,
    url: Union[Url | str],
    config_path: Union[Path | str] = Path("rss_feed_patterns.yml"),
) -> Optional[str]:
    try:
        if isinstance(url, str):
            url = parse_url(url)
        if isinstance(config_path, str):
            config_path = Path(config_path)
        # Load configuration
        if not config_path.is_absolute():
            config_path = Path(__file__).parent / config_path
        with open(config_path.absolute(), "r") as f:
            config = yaml.safe_load(f)

        hostname = url.host
        path = url.path

        for pattern in config["patterns"]:
            if "hostname" not in pattern:
                raise ValueError(f"Invalid {pattern}: missing hostname!")
            try:
                compiled = re.compile(pattern["hostname"], re.IGNORECASE)
            except re.error as e:
                raise ValueError(f'Invalid hostname regex: "{pattern["hostname"]}"{e}')
            if not compiled.match(hostname):
                continue
            if "path" in pattern:
                try:
                    compiled = re.compile(pattern["path"], re.IGNORECASE)
                except re.error as e:
                    raise ValueError(f'Invalid path regex: "{pattern["path"]}"{e}')
                match = compiled.match(path)
                if not match:
                    continue
                groups = match.groups()
            else:
                groups = ()

            rss_url = pattern["rss_url"]

            for i, group in enumerate(groups):
                rss_url = rss_url.replace(f"{{{i}}}", group)

            rss_url = rss_url.replace("{hostname}", hostname)
            rss_url = rss_url.replace("{package_name}", package_name)

            return rss_url
        print(f"No RSS URL configured for {hostname} with path {path}!")
    except Exception as e:
        print(f"Error getting RSS URL for {package_name} from {url}: {e}")
    return None


def get_release_monitoring(package_name: str, tarball_src: str) -> ReleaseMonitoring:
    tarball_uri = parse_url(tarball_src)

    if package_name.startswith("python-"):
        search_name = package_name[len("python-"):]
    else:
        search_name = package_name
    response = _get_release_exact_match(search_name, tarball_uri)
    return ReleaseMonitoring(
        YamlData(
            releases=Releases(
                response.get("id"), rss=get_known_rss_url(search_name, tarball_uri)
            ),
            security=_build_security(search_name),
        ),
        homepage=response.get("homepage"),
        name=response.get("name"),
        latest_version=response.get("version"),
    )


def _build_security(package: str) -> Security:
    results = check_cpe(package)
    if results:
        return Security(cpe=[Cpe(**items) for items in results])
    return Security(cpe=None)


def _is_pypi_project(url: Url):
    return url.hostname in [
        "files.pythonhosted.org",
        "pypi.org",
        "pypi.io",
        "pypi.debian.net",
    ]


def _get_release_exact_match(package_name: str, tarball_uri: Url) -> dict:
    base_url = "https://release-monitoring.org/api/v2/projects"
    items_per_page = 10
    ecosystem = f"{tarball_uri.scheme}://{tarball_uri.hostname}{'/'.join(tarball_uri.path.split('/')[:3])}"
    by_name_params = {"name": package_name, "items_per_page": items_per_page}
    by_ecosystem_params = {
        "ecosystem": ecosystem,
        "items_per_page": items_per_page,
    }

    for params in [by_name_params, by_ecosystem_params]:
        try:
            token = os.getenv("RELEASE_MONITORING_TOKEN")
            if not token:
                print(
                    "RELEASE_MONITORING_TOKEN environment variable is not set!"
                    "You can generate one at https://release-monitoring.org/settings"
                )
                return {}
            headers = {"Authorization": f"Token {token}"}
            result = requests.get(base_url, params=params, headers=headers)
            if result.status_code >= 500:
                print(f"Error {result.status_code} calling {base_url}!")
                break
            result.raise_for_status()
            project_search = result.json()

            if project_search.get("total_items") == 1:
                return project_search["items"][0]
            elif project_search.get("total_items") == items_per_page:
                # too vague
                continue
            elif project_search.get("total_items") > 1:
                # might be able to prevent the extra web call
                items = project_search["items"]
                # see if there's an exact name + ecosystem match
                for item in items:
                    if _is_pypi_project(tarball_uri):
                        eco_match = item["ecosystem"] == "pypi"
                    else:
                        eco_match = item["ecosystem"] == ecosystem

                    if item["name"].lower() == package_name and eco_match:
                        return item
        except Exception as e:
            print(f"Error checking release monitoring: {e}")

    return {}


if __name__ == "__main__":
    if len(argv) != 3:
        print(f"Usage: {argv[0]} <package_name> <tarball_src>")
        exit(1)
    result = get_release_monitoring(argv[1], argv[2])

    result.to_yaml("monitoring.yaml")
