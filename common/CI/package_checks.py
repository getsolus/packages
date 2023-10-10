#!/usr/bin/env python3
import argparse
import os.path
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TextIO
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

    def commit_refs(self, base: str, head: str) -> List[str]:
        return self.run_lines('log', '--pretty=%H', base + '..' + head)

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


class PackageDirectory(PullRequestCheck):
    _two_letter_dirs = ['py']
    _error = 'Package not in correct directory'
    _level = Level.ERROR

    def run(self) -> List[Result]:
        paths = [os.path.dirname(f) for f in self.package_files]

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


class Checker:
    checks = [
        Homepage,
        PackageBumped,
        PackageDirectory,
        Patch,
        UnwantedFiles,
        Pspec,
    ]

    def __init__(self, base: Optional[str], head: str, path: str, modified: bool, untracked: bool, files: List[str]):
        self.base = base
        self.head = head
        self.git = Git(path)
        self.files = self.git.relpaths(files)
        self.commits = []

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

        return len(errors) > 0

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
