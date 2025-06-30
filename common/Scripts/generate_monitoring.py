#!/usr/bin/env python3
import yaml
from pathlib import Path
from release_monitoring import get_release_monitoring


def read_package_yml():
    package_yml_path = Path("package.yml")
    if not package_yml_path.exists():
        raise FileNotFoundError("No package.yml found in current directory")

    with open(package_yml_path, "r") as f:
        return yaml.safe_load(f)


def extract_package_info(package_data):
    name = package_data.get("name")
    if not name:
        raise ValueError("No package name found in package.yml")

    source = package_data.get("source")
    if not source:
        raise ValueError("No source found in package.yml")
    source_url = list(source[0].keys())[0]

    return name, source_url


def main():
    package_data = read_package_yml()
    package_name, tarball_url = extract_package_info(package_data)

    print(f"Generating monitoring configuration for {package_name}")
    print(f"Source: {tarball_url}")

    result = get_release_monitoring(package_name, tarball_url)
    result.to_yaml("monitoring.yaml")

    print("Generated monitoring.yaml")

    if result.homepage:
        print(f"Homepage: {result.homepage}")
    if result.latest_version:
        print(f"Latest version: {result.latest_version}")


if __name__ == "__main__":
    main()
