#!/usr/bin/env python3
import argparse
import os.path
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, TextIO
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
        return self.run_lines('diff', '--name-only', '--diff-filter=AM',
                              self.merge_base(base, head), head)

    def fetch(self, remote: List[str]) -> None:
        self.run('fetch', *remote)

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
        return self.message.replace('\n', '%0A').replace('%', '%25')

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

    def __init__(self, git: Git):
        self.git = git

    def run(self, files: List[str]) -> List[Result]:
        raise NotImplementedError

    @staticmethod
    def _filter_packages(files: List[str]) -> List[str]:
        return [f for f in files if os.path.basename(f) in PullRequestCheck._package_files]

    def _path(self, path: str) -> str:
        return os.path.join(self.git.root, path)

    def _open(self, path: str) -> TextIO:
        return open(self._path(path), 'r')


class Homepage(PullRequestCheck):
    _error = '`homepage` is not set'
    _level = Level.ERROR

    def run(self, files: List[str]) -> List[Result]:
        return [Result(message=self._error, file=f, level=self._level)
                for f in self._filter_packages(files)
                if not self._includes_homepage(f)]

    def _includes_homepage(self, file: str) -> bool:
        with self._open(file) as f:
            return 'homepage' in yaml.safe_load(f)


class PackageDirectory(PullRequestCheck):
    _two_letter_dirs = ['py']
    _error = 'Package not in correct directory'
    _level = Level.ERROR

    def run(self, files: List[str]) -> List[Result]:
        paths = [os.path.dirname(f) for f in self._filter_packages(files)]

        return [Result(message=self._error, file=path, level=self._level) for path in paths
                if not self._check_path(path)]

    def _check_path(self, path: str) -> bool:
        pkg = os.path.basename(os.path.realpath(path))
        exp = ['packages', self._dir(pkg), pkg]

        return path.split('/') == exp

    def _dir(self, package: str) -> str:
        for two in self._two_letter_dirs:
            if package.startswith(two):
                return two

        return package[0]


class Patch(PullRequestCheck):
    _regex = r'patch -p1 <'
    _error = 'Uses `patch <`, use `patch -i` instead'
    _level = Level.ERROR

    def run(self, files: List[str]) -> List[Result]:
        return [r for f in self._filter_packages(files)
                for r in self._wrong_patch(f)]

    def _wrong_patch(self, file: str) -> List[Result]:
        results: List[Result] = []

        with self._open(file) as f:
            for i, line in enumerate(f.readlines()):
                if re.search(self._regex, line):
                    results.append(Result(message=self._error, file=file, line=i + 1, level=self._level))

        return results


class UnwantedFiles(PullRequestCheck):
    _patterns = ['Makefile^', r'.*\.eopkg^', r'.*\.tar\..*', r'^packages/[^/]+(/[^/]+)?$']
    _error = 'This file should not be included'
    _level = Level.ERROR

    def run(self, files: List[str]) -> List[Result]:
        return [Result(message=self._error, file=f, level=self._level)
                for f in files
                for p in self._patterns
                if not os.path.isdir(f) and re.match(p, f)]


class Pspec(PullRequestCheck):
    _error = '`package.yml` and `pspec_x86_64.xml` are not consistent, please rebuild.'
    _level = Level.ERROR

    def run(self, files: List[str]) -> List[Result]:
        paths = [os.path.dirname(f) for f in self._filter_packages(files)]

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


def run_checks(git: Git, files: List[str]) -> None:
    print(f'Checking files: {", ".join(files)}')

    checks = [Homepage(git), PackageDirectory(git), Patch(git), UnwantedFiles(git), Pspec(git)]
    results = [result for check in checks for result in check.run(files)]
    errors = [r for r in results if r.level == Level.ERROR]

    print(f"Found {len(results)} issue(s)")

    for result in results:
        print(result)

    if len(errors) > 0:
        exit(1)


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
    args = parser.parse_args()

    git = Git(args.root)
    args.filename = git.relpaths(args.filename)

    if args.base:
        git.fetch(_base_to_remote(args.base))
        args.filename += git.changed_files(args.base, args.head)

    if args.modified:
        args.filename += git.modified_files()

    if args.untracked:
        args.filename += git.untracked_files()

    run_checks(git, args.filename)
