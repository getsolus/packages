#!/usr/bin/env python3
import argparse
import glob
import json
import os.path
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TextIO, Tuple, Union
from urllib import request
from xml.etree import ElementTree

import yaml


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
        return self.run(*args).split("\n")

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


class Level(str, Enum):
    __str__ = Enum.__str__
    ERROR = 'error'
    WARNING = 'warning'


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
        return f'::{self.level}{self._meta}::{self._message}'

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


class PullRequestCheck:
    _package_files = ['package.yml']
    _two_letter_dirs = ['py']

    def __init__(self, git: Git, files: List[str], commits: List[str], base: Optional[str]):
        self.git = git
        self.files = files
        self.commits = commits
        self.base = base

    def run(self) -> List[Result]:
        raise NotImplementedError

    @property
    def package_files(self) -> List[str]:
        return self._filter_packages(self.files)

    def _filter_packages(self, files: List[str]) -> List[str]:
        return [f for f in files
                if os.path.basename(f) in self._package_files]

    def _path(self, path: str) -> str:
        return os.path.join(self.git.root, path)

    def _open(self, path: str) -> TextIO:
        return open(self._path(path), 'r')

    def load_package_yml(self, file: str) -> Dict[str, Any]:
        with self._open(file) as f:
            return dict(yaml.safe_load(f))

    def load_package_yml_from_commit(self, ref: str, file: str) -> Dict[str, Any]:
        return dict(yaml.safe_load(self.git.file_from_commit(ref, file)))

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


class Homepage(PullRequestCheck):
    _error = '`homepage` is not set'
    _level = Level.ERROR

    def run(self) -> List[Result]:
        return [Result(message=self._error, file=f, level=self._level)
                for f in self.package_files
                if not self._includes_homepage(f)]

    def _includes_homepage(self, file: str) -> bool:
        with self._open(file) as f:
            return 'homepage' in yaml.safe_load(f)


class PackageBumped(PullRequestCheck):
    _msg = 'Package release is not incremented by 1'
    _msg_new = 'Package release is not 1'
    _level = Level.WARNING

    def run(self) -> List[Result]:
        results = [self._check_commit(self.base or 'HEAD', file)
                   for file in self.package_files]

        return [result for result in results if result is not None]

    def _check_commit(self, base: str, file: str) -> Optional[Result]:
        new = self.load_package_yml(file)

        try:
            old = self.load_package_yml_from_commit(base, file)
            if int(old['release']) + 1 != int(new['release']):
                return Result(level=self._level, file=file, message=self._msg)

            return None
        except Exception as e:
            if 'exists on disk, but not in' in str(e):
                if int(new['release']) != 1:
                    return Result(level=self._level, file=file, message=self._msg_new)

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
            return Result(file=file, level=self._level, line=self.file_line(file, '^' + deps + r'\s*:'),
                          message=f'{deps} are not in order, expected: \n' + yaml.safe_dump(exp))

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

        if pkg.startswith('pkgconfig('):
            return 0, pkg.removeprefix('pkgconfig(')

        return 1, pkg


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
    _licenses: Optional[List[str]] = None
    _extra_licenses = ['Distributable', 'Public-Domain']
    _error = 'Invalid license identifier: '
    _level = Level.WARNING

    def run(self) -> List[Result]:
        return [r for f in self.package_files
                for r in self._validate_spdx(f) if r]

    def _validate_spdx(self, file: str) -> List[Optional[Result]]:
        license = self.load_package_yml(file)['license']
        if isinstance(license, list):
            return [self._validate_license(file, id) for id in license]

        return [self._validate_license(file, license)]

    def _validate_license(self, file: str, identifier: str) -> Optional[Result]:
        if identifier in self._license_ids():
            return None

        return Result(file=file, level=self._level,
                      message=f'invalid license identifier: {repr(identifier)}',
                      line=self.file_line(file, r'^license\s*:'))

    def _license_ids(self) -> List[str]:
        if self._licenses is None:
            with request.urlopen(self._licenses_url) as f:
                self._licenses = [license['licenseId'] for license in json.load(f)['licenses']]

        return self._licenses + self._extra_licenses


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
        xml = ElementTree.parse(self._xml_file(package_dir))
        xml_release = int(xml.findall('.//Update')[0].attrib['release'])
        xml_homepage: str = ''
        xml_homepage_element = xml.find('.//Homepage')

        if xml_homepage_element is not None:
            xml_homepage = xml_homepage_element.text or ''

        with open(self._yml_file(package_dir), 'r') as f:
            yml = yaml.safe_load(f)
            yml_release = yml.get('release', '')
            yml_homepage = yml.get('homepage', '')

        return bool(yml_release == xml_release and yml_homepage == xml_homepage)

    def _yml_file(self, package_dir: str) -> str:
        return self._path(os.path.join(package_dir, 'package.yml'))

    def _xml_file(self, package_dir: str) -> str:
        return self._path(os.path.join(package_dir, 'pspec_x86_64.xml'))


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
        return self._unwrap_component(self.load_package_yml(self.package_yml_path(pkg))['component'])

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

        return f"{package['name']}-{package['version']}-{package['release']}"

    def _commit_package_yaml(self, ref: str) -> Optional[Dict[str, Any]]:
        files = [f for f in self.git.files_in_commit(ref) if os.path.basename(f) == 'package.yml']
        if len(files) == 0:
            return None

        return self.load_package_yml_from_commit(ref, files[0])


class Checker:
    checks = [
        CommitMessage,
        Homepage,
        PackageBumped,
        PackageDependenciesOrder,
        PackageDirectory,
        Patch,
        Pspec,
        SPDXLicense,
        SystemDependencies,
        UnwantedFiles,
    ]

    def __init__(self, base: Optional[str], head: str, path: str, modified: bool, untracked: bool, files: List[str]):
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
        print(f'Checking files: {", ".join(self.files)}')
        if self.commits:
            print(f'Checking commits: {", ".join(self.commits)}')

        results = [result for check in self.checks
                   for result in check(self.git, self.files, self.commits, self.base).run()]
        errors = [r for r in results if r.level == Level.ERROR]

        print(f"Found {len(results)} result(s), {len(errors)} error(s)")

        for result in results:
            print(result)

        self.write_summary()

        return len(errors) > 0

    def write_summary(self) -> None:
        if self.summary_file is None:
            return

        with open(self.summary_file, 'w') as f:
            f.write(SummaryGenerator(self.git, self.files, self.commits, self.base).generate())

    @staticmethod
    def _base_to_remote(base: str) -> List[str]:
        return base.split('~')[0].split('/')


if __name__ == "__main__":
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
    parser.add_argument('filename', type=str, nargs="*",
                        help='Additional files to check')
    cli_args = parser.parse_args()
    checker = Checker(cli_args.base,
                      cli_args.head,
                      cli_args.root,
                      cli_args.modified,
                      cli_args.untracked,
                      cli_args.filename)
    exit(checker.run())
