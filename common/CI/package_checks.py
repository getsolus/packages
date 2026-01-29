#!/usr/bin/env python3
import argparse
import fnmatch
import glob
import json
import logging
import os.path
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from typing import Any, Callable, Dict, List, Optional, TextIO, Tuple, Union
from urllib import request
from xml.etree import ElementTree

"""Package is either a Package YML file or Pspec XML file."""
Package = Union['PackageYML', 'PspecXML']


def in_ci() -> bool:
    """Returns true if running in GitHub Actions or GitLab CI."""
    return os.environ.get('CI') == 'true'


class PackageYML:
    """Represents a Package YML file."""

    def __init__(self, stream: Any):
        yaml = YAML(typ='safe', pure=True)
        yaml.default_flow_style = False
        self._data = dict(yaml.load(stream))

    @property
    def name(self) -> str:
        return str(self._data['name'])

    @property
    def version(self) -> str:
        return str(self._data['version'])

    @property
    def release(self) -> int:
        return int(self._data['release'])

    @property
    def homepage(self) -> Optional[str]:
        return self._data.get('homepage')

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class PspecXML:
    """Represents a Pspec XML file."""

    def __init__(self, data: str):
        self._xml = ElementTree.fromstring(data)

    @property
    def release(self) -> int:
        return int(self._xml.findall('.//Update')[0].attrib['release'])

    @property
    def homepage(self) -> Optional[str]:
        xml_homepage_element = self._xml.find('.//Homepage')
        if xml_homepage_element is not None:
            return xml_homepage_element.text

        return None

    @property
    def files(self) -> List[str]:
        return [str(element.text) for element in self._xml.findall('.//Path')]


@dataclass
class FreezeConfig:
    start: Optional[datetime]
    end: Optional[datetime]

    def __init__(self, start: Optional[Union[str | datetime]], end: Optional[Union[str | datetime]]):
        self.start = datetime.fromisoformat(start) if isinstance(start, str) else start
        self.end = datetime.fromisoformat(end) if isinstance(end, str) else end

    def active(self) -> bool:
        now = datetime.now(tz=timezone.utc)

        return (self.start is not None and now > self.start and
                (self.end is None or now < self.end))


@dataclass
class StaticLibsConfig:
    """Configuration for the 'StaticLibs' check."""
    allowed_packages: List[str]
    allowed_files: List[str]


@dataclass
class Config:
    freeze: FreezeConfig
    static_libs: StaticLibsConfig

    @staticmethod
    def load(stream: Any) -> 'Config':
        yaml = YAML(typ='safe', pure=True)
        return Config(**yaml.load(stream))

    def __post_init__(self) -> None:
        self.freeze = FreezeConfig(**self.freeze)  # type: ignore
        self.static_libs = StaticLibsConfig(**self.static_libs)  # type: ignore


class Git:
    def __init__(self, path: str):
        self.path = path
        self.root = self._run(path, ['rev-parse', '--show-toplevel'])

    @staticmethod
    def _run(path: str, args: List[str]) -> str:
        res = subprocess.run(['git', '-C', path] + args, capture_output=True, text=True)
        if res.returncode != 0:
            raise Exception("git error: " + res.stderr)

        return res.stdout.strip()

    def run(self, *args: str) -> str:
        return self._run(self.root, list(args))

    def run_lines(self, *args: str) -> List[str]:
        return self.run(*args).splitlines()

    def changed_files(self, base: str, head: str) -> List[str]:
        return self.run_lines('diff', '--name-only', '--diff-filter=AM', base, head)

    def commit_message(self, ref: str) -> str:
        return self.run('log', '-1', '--format=%B', ref)

    def commit_refs(self, base: str, head: str) -> List[str]:
        return self.run_lines('log', '--no-merges', '--pretty=%H', base + '..' + head)

    def fetch(self, remote: List[str]) -> None:
        self.run('fetch', *remote)

    def file_from_commit(self, ref: str, file: str) -> str:
        return self.run('show', f'{ref}:{file}')

    def files_in_commit(self, ref: str) -> List[str]:
        return self.changed_files(ref + '~', ref)

    def merge_base(self, head: str, base: str) -> str:
        return self.run('merge-base', head, base)

    def modified_files(self) -> List[str]:
        return self.run_lines('ls-files', '--others', '--exclude-standard', self.root)

    def relpaths(self, files: List[str]) -> List[str]:
        return [os.path.relpath(os.path.realpath(f), self.root) for f in files]

    def untracked_files(self) -> List[str]:
        return self.run_lines('diff', '--name-only', '--diff-filter=AM')


class LogFormatter(logging.Formatter):
    fmt = '\033[0m \033[94m%(pathname)s:%(lineno)d:\033[0m %(message)s'
    formatters = {
        logging.DEBUG: logging.Formatter('\033[1;30mDBG' + fmt),
        logging.INFO: logging.Formatter('\033[34mINF' + fmt),
        logging.WARNING: logging.Formatter('\033[33mWRN' + fmt),
        logging.ERROR: logging.Formatter('\033[31mERR' + fmt),
        logging.CRITICAL: logging.Formatter('\033[31mCRI' + fmt),
    }

    def format(self, record: logging.LogRecord) -> str:
        return self.formatters[record.levelno].format(record)

    @staticmethod
    def handler() -> logging.Handler:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(LogFormatter())

        return handler


class Level(str, Enum):
    __str__ = Enum.__str__
    DEBUG = 'debug'
    NOTICE = 'notice'
    ERROR = 'error'
    WARNING = 'warning'

    @property
    def log_level(self) -> int:
        match self:
            case Level.DEBUG:
                return logging.DEBUG
            case Level.NOTICE:
                return logging.INFO
            case Level.WARNING:
                return logging.WARNING
            case Level.ERROR:
                return logging.ERROR
            case _:
                return 0


@dataclass
class Result:
    level: Level
    message: str
    title: Optional[str] = None
    file: Optional[str] = None
    col: Optional[int] = None
    endColumn: Optional[int] = None
    line: Optional[int] = None
    endLine: Optional[int] = None

    def __str__(self) -> str:
        return f'::{self.level.value}{self._meta}::{self._message}'

    def log(self) -> None:
        if in_ci():
            print(str(self))
            return

        logging.getLogger(__name__).handle(self._record)

    @property
    def _message(self) -> str:
        return self.message.replace('%', '%25').replace('\n', '%0A')

    @property
    def _meta(self) -> str:
        attrs = ['title', 'file', 'col', 'endColumn', 'line', 'endLine']
        meta = [self._property(key) for key in attrs
                if self._property(key) != '']
        if len(meta) == 0:
            return ''

        return ' ' + ",".join(meta)

    def _property(self, key: str) -> str:
        value = getattr(self, key)
        if value is None:
            return ''

        return f'{key}={value}'

    @property
    def _record(self) -> logging.LogRecord:
        return logging.LogRecord('',
                                 self.level.log_level,
                                 self.file or '',
                                 self.line or 1,
                                 self.message,
                                 None, None)


class PullRequestCheck:
    _package_files = ['package.yml']
    _two_letter_dirs = ['py']
    _config: Optional[Config] = None

    def __init__(self, git: Git, files: List[str], commits: List[str], base: Optional[str]):
        self.git = git
        self.files = files
        self.commits = commits
        self.base = base

    def run(self) -> List[Result]:
        raise NotImplementedError

    @property
    def config(self) -> Config:
        if self._config is None:
            with self._open(os.path.join('common', 'CI', 'config.yaml')) as f:
                self._config = Config.load(f)

        return self._config

    @property
    def package_files(self) -> List[str]:
        return self.filter_files(*self._package_files)

    def filter_files(self, *allowed: str) -> List[str]:
        return [f for f in self.files
                if os.path.basename(f) in allowed]

    def _path(self, path: str) -> str:
        return os.path.join(self.git.root, path)

    def _open(self, path: str) -> TextIO:
        return open(self._path(path), 'r')

    def _read(self, path: str) -> str:
        with self._open(path) as f:
            return str(f.read())

    def _exists(self, path: str) -> bool:
        return os.path.exists(self._path(path))

    def load_package_yml(self, file: str) -> PackageYML:
        with self._open(file) as f:
            return PackageYML(f)

    def load_package_yml_from_commit(self, ref: str, file: str) -> PackageYML:
        return PackageYML(self.git.file_from_commit(ref, file))

    def load_pspec_xml(self, file: str) -> PspecXML:
        return PspecXML(self._read(file))

    def load_pspec_xml_from_commit(self, ref: str, file: str) -> PspecXML:
        return PspecXML(self.git.file_from_commit(ref, file))

    def file_line(self, file: str, expr: str) -> Optional[int]:
        with self._open(file) as f:
            for i, line in enumerate(f.read().splitlines()):
                if re.match(expr, line):
                    return i + 1

        return None

    def package_file_line(self, package: str, file: str, expr: str) -> Optional[int]:
        return self.file_line(self.package_file(package, file), expr)

    def package_yml_path(self, package: str) -> str:
        return self.package_file(package, 'package.yml')

    def package_file(self, package: str, file: str) -> str:
        return os.path.join(self.package_dir(package), file)

    def package_dir(self, package: str) -> str:
        return os.path.join('packages', self._package_subdir(package), package)

    @staticmethod
    def package_for(path: str) -> str:
        parts = path.split("/")
        if len(parts) < 3 or parts[0] != "packages":
            return ""

        return parts[2]

    def _package_subdir(self, package: str) -> str:
        package = package.lower()

        for two in self._two_letter_dirs:
            if package.startswith(two):
                return two

        return package[0]


class CommitMessage(PullRequestCheck):
    def run(self) -> List[Result]:
        return [result
                for commit in self.commits
                for result in self._check_commit(commit)]

    def _check_commit(self, commit: str) -> List[Result]:
        msg = self.git.commit_message(commit)
        files = self.git.files_in_commit(commit)
        file = files[0] if files else ''

        results: List[Result] = []

        if msg.strip().endswith(']'):
            results.append(Result(message='commit ends with ]', level=Level.ERROR, file=file))

        return results


class FrozenPackage(PullRequestCheck):
    __packages: Optional[List[str]] = None
    __message_normal = ('This package is included in the ISO. '
                        'Consider validating the functionality in a newly built ISO.')
    __message_freeze = ('This package is included in the ISO and is currently frozen. '
                        'It can only be updated to fix critical bugs, '
                        'in consultation with multiple Solus staff members.')

    def run(self) -> List[Result]:
        return [self._make_result(f)
                for f in self.package_files
                if self._is_frozen(f)]

    def _make_result(self, file: str) -> Result:
        if self.config.freeze.active():
            return Result(message=self.__message_freeze, file=file, level=Level.WARNING)

        return Result(message=self.__message_normal, file=file, level=Level.NOTICE)

    def _is_frozen(self, file: str) -> bool:
        return self.package_for(file) in self._packages()

    def _packages(self) -> List[str]:
        if self.__packages is None:
            with self._open(os.path.join('common', 'iso_packages.txt')) as file:
                self.__packages = [line.strip() for line in file]

        return self.__packages


class Homepage(PullRequestCheck):
    _error = '`homepage` is not set'
    _level = Level.ERROR

    def run(self) -> List[Result]:
        return [Result(message=self._error, file=f, level=self._level)
                for f in self.package_files
                if not self._includes_homepage(f)]

    def _includes_homepage(self, file: str) -> bool:
        with self._open(file) as f:
            yaml = YAML(typ='safe', pure=True)
            yaml.default_flow_style = False
            return 'homepage' in yaml.load(f)


class BooleanStyle(PullRequestCheck):
    _error = 'Invalid boolean style. Use true/false instead.'
    _level = Level.ERROR
    _pattern = re.compile(r':\s*(yes|no)\s*$', re.IGNORECASE)

    def run(self) -> List[Result]:
        results: List[Result] = []

        for f in self.package_files:
            with self._open(f) as stream:
                for i, line in enumerate(stream.readlines(), start=1):
                    if self._pattern.search(line):
                        results.append(Result(
                            message=self._error,
                            file=f,
                            line=i,
                            level=self._level
                          ))

        return results


class Monitoring(PullRequestCheck):
    _error = '`monitoring.yaml` is missing'
    _level = Level.WARNING

    def run(self) -> List[Result]:
        return [Result(message=self._error, file=f, level=self._level)
                for f in self.package_files
                if not self._has_monitoring_yml(f)]

    def _has_monitoring_yml(self, file: str) -> bool:
        return self._exists(os.path.join(os.path.dirname(file), 'monitoring.yaml'))


class PackageBumped(PullRequestCheck):
    _msg = 'Package release is not incremented by 1'
    _msg_new = 'Package release is not 1'

    def run(self) -> List[Result]:
        commits = self.commits or ['HEAD']
        files = set(self.files) & set(self.git.untracked_files() + self.git.modified_files())

        results = []
        with ThreadPoolExecutor() as executor:
            futures = []

            # commit-based checks
            for commit in commits:
                for file in self.git.files_in_commit(commit):
                    futures.append(executor.submit(self._check_commit, commit, file))

            # file-based checks
            for file in files:
                futures.append(executor.submit(self._check_commit, None, file))

        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)

        return results

    def _check_commit(self, ref: Optional[str], file: str) -> Optional[Result]:
        match os.path.basename(file):
            case 'package.yml':
                return self._check(ref, file, PackageYML, Level.WARNING)
            case 'pspec_x86_64.xml':
                return self._check(ref, file, PspecXML, Level.ERROR)
            case _:
                return None

    def _is_fixup_commit(self, commit_msg: str) -> bool:
        return commit_msg.startswith('fixup! ')

    def _check(self, ref: Optional[str], file: str, loader: Callable[[str], Package], level: Level) -> Optional[Result]:
        if ref is not None:
            new = loader(self.git.file_from_commit(ref, file))
            prev = f'{ref}~1'

            commit_msg = self.git.commit_message(ref)
            # Skip fixup commits entirely
            if self._is_fixup_commit(commit_msg):
                return None
        else:
            new = loader(self._read(file))
            prev = 'HEAD'

        try:
            old = loader(self.git.file_from_commit(prev, file))
            # Skip if this is effectively an amended commit with no release change
            if ref is not None and self.git.commit_message(ref) == self.git.commit_message(prev):
                return None

            if old.release + 1 != new.release:
                return Result(level=level, file=file, message=f'{self._msg} (ref: {ref})')

            return None
        except Exception as e:
            if 'exists on disk, but not in' in str(e):
                if new.release != 1:
                    return Result(level=level, file=file, message=f'{self._msg_new} (ref: {ref})')

                return None

            raise e


class PackageDependenciesOrder(PullRequestCheck):
    _deps_keys = ['builddeps', 'checkdeps', 'rundeps']
    _error = '`` are not in order'
    _level = Level.WARNING

    def run(self) -> List[Result]:
        results = [self._check_deps(deps, file)
                   for deps in self._deps_keys
                   for file in self.package_files]

        return [result for result in results if result is not None]

    def _check_deps(self, deps: str, file: str) -> Optional[Result]:
        cur = self.load_package_yml(file).get(deps, [])
        exp = self._sorted(cur)

        if cur != exp:
            class Dumper(YAML):
                def dump(self, data: Any, stream: Optional[StringIO] = None, **kw: int) -> Any:
                    self.default_flow_style = False
                    self.indent(offset=4, sequence=4)
                    self.prefix_colon = ' '  # type: ignore[assignment]
                    stream = StringIO()
                    YAML.dump(self, data, stream, **kw)
                    return stream.getvalue()

            yaml = Dumper(typ='safe', pure=True)
            return Result(file=file, level=self._level, line=self.file_line(file, '^' + deps + r'\s*:'),
                          message=f'{deps} are not in order, expected: \n' + yaml.dump(exp))

        return None

    @staticmethod
    def _sorted(deps: List[Union[str, Dict[str, List[str]]]]) -> List[Union[str, Dict[str, List[str]]]]:
        for dep in deps:
            if isinstance(dep, dict):
                for k, v in dep.items():
                    if isinstance(v, str):
                        dep[k] = v
                    else:
                        dep[k] = sorted(v, key=PackageDependenciesOrder._sort)

        return sorted(deps, key=PackageDependenciesOrder._sort)

    @staticmethod
    def _sort(pkg: Union[str, Dict[str, List[str]]]) -> Tuple[int, str]:
        if isinstance(pkg, dict):
            pkg = list(pkg.keys())[0]

        if pkg.startswith('pkgconfig32('):
            return 0, pkg.removeprefix('pkgconfig32(')

        if pkg.startswith('pkgconfig('):
            return 1, pkg.removeprefix('pkgconfig(')

        return 2, pkg


class PackageDirectory(PullRequestCheck):
    _error = 'Package not in correct directory'
    _level = Level.ERROR

    def run(self) -> List[Result]:
        paths = [os.path.dirname(f) for f in self.package_files]

        return [Result(message=self._error, file=path, level=self._level) for path in paths
                if not self._check_path(path)]

    def _check_path(self, path: str) -> bool:
        pkg = os.path.basename(os.path.realpath(path))
        exp = ['packages', self._package_subdir(pkg), pkg]

        return path.split('/') == exp


class PackageVersion(PullRequestCheck):
    _error = 'Package version is not a string'
    _level = Level.ERROR

    def run(self) -> List[Result]:
        return [Result(message=self._error, level=self._level,
                       file=path, line=self.file_line(path, r'^version\s*:'), )
                for path in self.package_files
                if not self._check_version(path)]

    def _check_version(self, path: str) -> bool:
        return isinstance(self.load_package_yml(path).version, str)


class Patch(PullRequestCheck):
    _regex = r'patch -p1 <'
    _error = 'Uses `patch <`, use `patch -i` instead'
    _level = Level.ERROR

    def run(self) -> List[Result]:
        return [r for f in self.package_files
                for r in self._wrong_patch(f)]

    def _wrong_patch(self, file: str) -> List[Result]:
        results: List[Result] = []

        with self._open(file) as f:
            for i, line in enumerate(f.readlines()):
                if re.search(self._regex, line):
                    results.append(Result(message=self._error, file=file, line=i + 1, level=self._level))

        return results


class SPDXLicense(PullRequestCheck):
    _licenses_url = 'https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json'
    _exceptions_url = 'https://raw.githubusercontent.com/spdx/license-list-data/main/json/exceptions.json'
    _licenses: Optional[List[str]] = None
    _exceptions: Optional[List[str]] = None
    _extra_licenses = ['Distributable', 'EULA', 'Public-Domain']
    _error = 'Invalid license identifier: '
    _level = Level.WARNING

    def run(self) -> List[Result]:
        return [r for f in self.package_files
                for r in self._validate_spdx(f) if r]

    def _validate_spdx(self, file: str) -> List[Optional[Result]]:
        license = self.load_package_yml(file).get('license')
        if isinstance(license, list):
            return [self._validate_license(file, id) for id in license]

        return [self._validate_license(file, license)]

    def _validate_license(self, file: str, identifier: str) -> Optional[Result]:
        if self._valid_license(identifier):
            return None

        return Result(file=file, level=self._level,
                      message=f'invalid license identifier: {repr(identifier)}',
                      line=self.file_line(file, r'^license\s*:'))

    def _valid_license(self, identifier: str) -> bool:
        identifier = identifier.strip(" ()+")
        identifiers = [id_o
                       for id_a in identifier.split(' AND ')
                       for id_o in id_a.split(' OR ')]

        if len(identifiers) > 1:
            return all([self._valid_license(id) for id in identifiers])

        if ' WITH ' in identifier:
            identifier, exception = identifier.split(' WITH ', 1)

            if exception not in self._exception_ids():
                return False

        return identifier in self._license_ids()

    def _license_ids(self) -> List[str]:
        if self._licenses is None:
            with request.urlopen(self._licenses_url) as f:
                self._licenses = [license['licenseId'] for license in json.load(f)['licenses']]

        return self._licenses + self._extra_licenses

    def _exception_ids(self) -> List[str]:
        if self._exceptions is None:
            with request.urlopen(self._exceptions_url) as f:
                self._exceptions = [exception['licenseExceptionId'] for exception in json.load(f)['exceptions']]

        return self._exceptions


class UnwantedFiles(PullRequestCheck):
    _patterns = ['Makefile^', r'.*\.eopkg^', r'.*\.tar\..*', r'^packages/[^/]+(/[^/]+)?$']
    _error = 'This file should not be included'
    _level = Level.ERROR

    def run(self) -> List[Result]:
        return [Result(message=self._error, file=f, level=self._level)
                for f in self.files
                for p in self._patterns
                if not os.path.isdir(f) and re.match(p, f)]


class Pspec(PullRequestCheck):
    _error = '`package.yml` and `pspec_x86_64.xml` are not consistent, please rebuild.'
    _level = Level.ERROR

    def run(self) -> List[Result]:
        paths = [os.path.dirname(f) for f in self.package_files]

        return [Result(message=self._error, file=os.path.join(path, 'pspec_x86_64.xml'), level=self._level)
                for path in paths
                if not self._check_consistent(path)]

    def _check_consistent(self, package_dir: str) -> bool:
        xml = self._xml_file(package_dir)
        yml = self._yml_file(package_dir)

        return bool(yml.release == xml.release and yml.homepage == xml.homepage)

    def _yml_file(self, package_dir: str) -> PackageYML:
        return self.load_package_yml(os.path.join(package_dir, 'package.yml'))

    def _xml_file(self, package_dir: str) -> PspecXML:
        return self.load_pspec_xml(os.path.join(package_dir, 'pspec_x86_64.xml'))


class StaticLibs(PullRequestCheck):
    """
    Checks if any static libraries have been included.

    Static libraries can be allowed by adding them to the allow list.
    """
    _error = 'A static library has been included in the package.'
    _level = Level.ERROR

    def run(self) -> List[Result]:
        return [self._result(pspec, file)
                for pspec in self.filter_files('pspec_x86_64.xml')
                if not self._allowed_package(pspec)
                for file in self.load_pspec_xml(pspec).files
                if self._check(file)]

    def _result(self, pspec: str, file: str) -> Result:
        return Result(message=f'A static library has been included in the package: `{file}`. '
                              'Whitelist the package or file in `common/CI/config.yaml` if this is desired.',
                      file=pspec, line=self.file_line(pspec, f'.*{file}.*'), level=self._level)

    def _check(self, file: str) -> bool:
        return (file.startswith('/usr/lib') and
                file.endswith('.a') and
                not self._allowed_path(file))

    def _allowed_package(self, file: str) -> bool:
        return self.package_for(file) in self.config.static_libs.allowed_packages

    def _allowed_path(self, file: str) -> bool:
        return any([fnmatch.filter([file], pattern)
                    for pattern in self.config.static_libs.allowed_files])


class SystemDependencies(PullRequestCheck):
    _components = ['system.base', 'system.devel']

    def run(self) -> List[Result]:
        return [result
                for f in self.package_files
                for result in self._check_deps(f)]

    def _check_deps(self, pkg_file: str) -> List[Result]:
        pkg = os.path.basename(os.path.dirname(pkg_file))
        pkg_components = self._package_components(pkg)

        return self._validate_deps(pkg) if self._components_match(pkg_components) else []

    def _package_components(self, pkg: str) -> List[str]:
        return self._unwrap_component(self.load_package_yml(self.package_yml_path(pkg)).get('component'))

    def _unwrap_component(self, component: Any) -> List[str]:
        if isinstance(component, dict):
            return [c for v in component.values() for c in self._unwrap_component(v)]

        if isinstance(component, list):
            return [c for item in component for c in self._unwrap_component(item)]

        return [component]

    def _validate_deps(self, pkg: str) -> List[Result]:
        libs_file = self.package_file(pkg, 'abi_used_libs')
        if not os.path.exists(libs_file):
            return []

        with self._open(libs_file) as f:
            results = {package: (lib, self._components_match(self._package_components(package)))
                       for lib, package in set([self._search_lib(lib.strip()) for lib in f])
                       if package is not None}

            return [Result(message=f'Dependency not in system.base/devel: {dep}',
                           level=Level.WARNING, file=libs_file,
                           line=self.package_file_line(pkg, 'abi_used_libs', f'^{lib}$'))
                    for dep, (lib, check) in results.items() if not check]

    def _components_match(self, components: List[str]) -> bool:
        return len(set(components) & set(self._components)) > 0

    def _search_lib(self, name: str) -> Tuple[str, Optional[str]]:
        for f in glob.glob(self._path(os.path.join('packages', '*', '*', 'abi_libs'))):
            with open(f, 'r') as libs:
                for lib in libs:
                    if lib.strip() == name:
                        return name, os.path.basename(os.path.dirname(f))

        return name, None


class SummaryGenerator(PullRequestCheck):
    def generate(self) -> str:
        s = "# Changelog entries\n\n"

        for commit in self.commits:
            package_tag = self._commit_package_tag(commit)
            if package_tag is None:
                continue

            s += f"## {package_tag}\n\n"
            s += self.git.commit_message(commit) + "\n\n"

        return s

    def _commit_package_tag(self, ref: str) -> Optional[str]:
        package = self._commit_package_yaml(ref)
        if package is None:
            return None

        return f"{package.name}-{package.version}-{package.release}"

    def _commit_package_yaml(self, ref: str) -> Optional[PackageYML]:
        files = [f for f in self.git.files_in_commit(ref) if os.path.basename(f) == 'package.yml']
        if len(files) == 0:
            return None

        return self.load_package_yml_from_commit(ref, files[0])


class Checker:
    checks = [
        BooleanStyle,
        CommitMessage,
        FrozenPackage,
        Homepage,
        Monitoring,
        PackageBumped,
        PackageDependenciesOrder,
        PackageDirectory,
        PackageVersion,
        Patch,
        Pspec,
        SPDXLicense,
        StaticLibs,
        SystemDependencies,
        UnwantedFiles,
    ]

    def __init__(self, base: Optional[str], head: str, path: str, files: List[str],
                 modified: bool, untracked: bool, results_only: bool, exit_warn: bool):
        self.results_only = results_only
        self.exit_warn = exit_warn
        self.base = base
        self.head = head
        self.git = Git(path)
        self.files = self.git.relpaths(files)
        self.commits = []
        self.summary_file = os.environ.get('GITHUB_STEP_SUMMARY', None)

        if base is not None:
            self.git.fetch(self._base_to_remote(base))
            self.files += self.git.changed_files(self.git.merge_base(base, head), head)
            self.commits = self.git.commit_refs(self.git.merge_base(base, head), head)

        if modified:
            self.files += self.git.modified_files()

        if untracked:
            self.files += self.git.untracked_files()

    def run(self) -> bool:
        if not self.results_only:
            print(f'Checking files: {", ".join(self.files)}')
            if self.commits:
                print(f'Checking commits: {", ".join(self.commits)}')

        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(
                    check(self.git, self.files, self.commits, self.base).run
                )
                for check in self.checks
            ]

        results = []
        for future in as_completed(futures):
            results.extend(future.result())

        errors = [r for r in results if r.level == Level.ERROR]
        warnings = [r for r in results if r.level == Level.WARNING]

        if not self.results_only:
            print(f"Found {len(results)} result(s), {len(warnings)} warnings and {len(errors)} error(s)")

        for result in results:
            result.log()

        self.write_summary()

        return len(errors) > 0 or self.exit_warn and len(warnings) > 0

    def write_summary(self) -> None:
        if self.summary_file is None:
            return

        with open(self.summary_file, 'w') as f:
            f.write(SummaryGenerator(self.git, self.files, self.commits, self.base).generate())

    @staticmethod
    def _base_to_remote(base: str) -> List[str]:
        return base.split('~')[0].split('/')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[LogFormatter.handler()])

    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=str,
                        help='Optional reference to the base branch')
    parser.add_argument('--head', type=str, default='HEAD',
                        help='Optional reference to the current branch head')
    parser.add_argument('--root', type=str, default='.',
                        help='Repository root directory')
    parser.add_argument('--modified', action='store_true',
                        help='Include modified files')
    parser.add_argument('--untracked', action='store_true',
                        help='Include untracked files')
    parser.add_argument('--fail-on-warnings', action='store_true',
                        help='Exit with an error if warnings are encountered')
    parser.add_argument('--results-only', action='store_true',
                        help='Only show results, nothing else')
    parser.add_argument('filename', type=str, nargs="*",
                        help='Additional files to check')

    cli_args = parser.parse_args()
    checker = Checker(base=cli_args.base,
                      head=cli_args.head,
                      path=cli_args.root,
                      modified=cli_args.modified,
                      untracked=cli_args.untracked,
                      files=cli_args.filename,
                      results_only=cli_args.results_only,
                      exit_warn=cli_args.fail_on_warnings)
    exit(checker.run())
