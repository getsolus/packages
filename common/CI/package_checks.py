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


class Level(str, Enum):
    __str__ = Enum.__str__
    ERROR = 'error'
    WARNING = 'warning'


@dataclass
class Result:
    message: str
    file: str
    line: Optional[int]
    level: Level

    def __str__(self) -> str:
        if self.file:
            if self.line:
                return f'::{self.level} file={self.file},line={self.line}::{self.message}'
            return f'::{self.level} file={self.file}::{self.message}'

        return f'::{self.level}::{self.message}'


class PullRequestCheck:
    _package_files = ['package.yml']

    def __init__(self, root: str):
        self._root = root

    def run(self, files: List[str]) -> List[Result]:
        raise NotImplementedError

    @staticmethod
    def _filter_packages(files: List[str]) -> List[str]:
        return [f for f in files if os.path.basename(f) in PullRequestCheck._package_files]

    def _path(self, path: str) -> str:
        return os.path.join(self._root, path)

    def _open(self, path: str) -> TextIO:
        return open(self._path(path), 'r')


class Homepage(PullRequestCheck):
    _error = '`homepage` is not set'
    _level = Level.ERROR

    def run(self, files: List[str]) -> List[Result]:
        return [Result(self._error, f, None, self._level)
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

        return [Result(self._error, path, None, self._level) for path in paths
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
                    results.append(Result(self._error, file, i + 1, self._level))

        return results


class UnwantedFiles(PullRequestCheck):
    _patterns = ['Makefile^', r'.*\.eopkg^', r'.*\.tar\..*', r'^packages/[^/]+(/[^/]+)?$']
    _error = 'This file should not be included'
    _level = Level.ERROR

    def run(self, files: List[str]) -> List[Result]:
        return [Result(self._error, f, None, self._level)
                for f in files
                for p in self._patterns
                if not os.path.isdir(f) and re.match(p, f)]


class Pspec(PullRequestCheck):
    _error = '`package.yml` and `pspec_x86_64.xml` are not consistent, please rebuild.'
    _level = Level.ERROR

    def run(self, files: List[str]) -> List[Result]:
        paths = [os.path.dirname(f) for f in self._filter_packages(files)]

        return [Result(self._error, os.path.join(path, 'pspec_x86_64.xml'), None, self._level)
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


def run_checks(root: str, files: List[str]) -> None:
    print(f'Checking files: {", ".join(files)}')

    checks = [Homepage(root), PackageDirectory(root), Patch(root), UnwantedFiles(root), Pspec(root)]
    results = [result for check in checks for result in check.run(files)]
    errors = [r for r in results if r.level == Level.ERROR]

    print(f"Found {len(results)} issue(s)")

    for result in results:
        print(result)

    if len(errors) > 0:
        exit(1)


def _git(dir: str, args: List[str]) -> str:
    res = subprocess.run(['git', '-C', dir] + args, capture_output=True, text=True)
    if res.returncode != 0:
        raise Exception("git error: " + res.stderr)

    return res.stdout.strip()


def _git_root(dir: str) -> str:
    return _git(dir, ['rev-parse', '--show-toplevel'])


def _ref_to_fetch(ref: str) -> List[str]:
    return ref.split('..')[0].split('/')


def files_from_ref(root: str, base: str, head: str) -> List[str]:
    _git(root, ['fetch'] + _ref_to_fetch(base))

    merge_base = _git(root, ['merge-base', head, base])

    return _git(root, ['diff', '--name-only', '--diff-filter=AM', merge_base, head]).split("\n")


def repo_relative_paths(root: str, files: List[str]) -> List[str]:
    return [os.path.relpath(os.path.realpath(f), root) for f in files]


def modified_files(root: str) -> List[str]:
    return _git(root, ['ls-files', '--others',  '--exclude-standard', root]).split("\n")


def untracked_files(root: str) -> List[str]:
    return _git(root, ['diff', '--name-only', '--diff-filter=AM']).split("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=str,
                        help='Optional reference to the base branch')
    parser.add_argument('--head', type=str, default='HEAD',
                        help='Optional reference to the current branch head')
    parser.add_argument('--root', type=str, default=_git_root('.'),
                        help='Repository root directory')
    parser.add_argument('--modified', action='store_true',
                        help='Include modified files')
    parser.add_argument('--untracked', action='store_true',
                        help='Include untracked files')
    parser.add_argument('filename', type=str, nargs="*",
                        help='Additional files to check')
    args = parser.parse_args()
    args.filename = repo_relative_paths(args.root, args.filename)

    if args.base:
        args.filename += files_from_ref(args.root, args.base, args.head)

    if args.modified:
        args.filename += modified_files(args.root)

    if args.untracked:
        args.filename += untracked_files(args.root)

    run_checks(args.root, args.filename)
