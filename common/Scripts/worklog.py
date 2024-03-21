#!/usr/bin/env python3
import argparse
import json
import os.path
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence
from urllib import request


class TTY:
    Reset = '\033[0m'
    Red = '\033[31m'
    Green = '\033[32m'
    Yellow = '\033[33m'
    Blue = '\033[34m'
    White = '\033[97m'

    @staticmethod
    def url(name: str, ref: str) -> str:
        return f'\033]8;;{ref}\033\\{name}\033]8;;\033\\'


class Listable:
    @property
    def package(self) -> str:
        raise NotImplementedError

    @property
    def date(self) -> datetime:
        raise NotImplementedError

    def to_md(self) -> str:
        raise NotImplementedError

    def to_tty(self) -> str:
        raise NotImplementedError


class GitHubCommit:
    @staticmethod
    def get(ref: str) -> 'GitHubCommit':
        cached = GitHubCommit.__get_cache(ref)
        if cached is not None:
            return cached

        return GitHubCommit.__get_gh_cli(ref)

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def author(self) -> str:
        author = self._data.get('author')
        if author is not None:
            return str(author.get('login', 'Unknown'))

        return str(self._data['commit']['author']['name'])

    @staticmethod
    def __tempfile(ref: str) -> str:
        dir = os.path.join(tempfile.gettempdir(), '_solus_worklog')
        os.makedirs(dir, exist_ok=True, mode=0o700)

        return os.path.join(dir, ref + '.json')

    @staticmethod
    def __get_cache(ref: str) -> Optional['GitHubCommit']:
        file = GitHubCommit.__tempfile(ref)
        if not os.path.exists(file):
            return None

        with open(file, 'rb') as f:
            return GitHubCommit(json.loads(f.read()))

    @staticmethod
    def __store_cache(ref: str, commit: str) -> None:
        with open(os.path.join(GitHubCommit.__tempfile(ref)), 'w') as fh:
            fh.write(commit)

    @staticmethod
    def __get_gh_cli(ref: str) -> 'GitHubCommit':
        res = subprocess.run(['gh', 'api', f'repos/getsolus/packages/commits/{ref}'],
                             capture_output=True, text=True)
        if res.returncode != 0:
            raise ValueError(f'GitHub API returned non-zero exit: {res.stderr}')

        GitHubCommit.__store_cache(ref, res.stdout)

        return GitHubCommit(json.loads(res.stdout))


@dataclass
class Build(Listable):
    id: int
    pkg: str
    version: str
    release: str
    ref: str
    tag: str
    tag_url: str
    log_url: str
    status: str
    builder: str
    finished: Optional[str]

    @property
    def package(self) -> str:
        return self.pkg

    @property
    def date(self) -> datetime:
        if self.finished is None:
            return datetime.now(tz=timezone.utc)

        return datetime.fromisoformat(self.finished).astimezone(timezone.utc)

    def to_md(self) -> str:
        return f'[{self.pkg} {self.v}]({self.tag_url})'

    def to_tty(self) -> str:
        return (f'{TTY.Green}{self.pkg}{TTY.Reset} {self.v} ' +
                f'{TTY.Blue}[{self.builder}]{TTY.Reset} ' +
                TTY.url('[🡕]', self.tag_url))

    @property
    def v(self) -> str:
        return f'{self.version}-{self.release}'

    def commit(self) -> GitHubCommit:
        return GitHubCommit.get(self.ref)


class Update(Listable):
    """
    Update represents a package update.
    It includes information from one or more builds.
    """

    def __init__(self, *builds: Build):
        self.builds = list(builds)

    def append(self, build: Build) -> None:
        self.builds.append(build)

    @property
    def last(self) -> Build:
        return max(self.builds, key=lambda b: b.date)

    @property
    def date(self) -> datetime:
        return self.last.date

    @property
    def package(self) -> str:
        return self.last.package

    @property
    def v(self) -> str:
        return self.last.v

    @property
    def _successful_builds(self) -> Iterable[Build]:
        return [build for build in self.builds if build.status == "OK"]

    def to_tty(self) -> str:
        authors = [TTY.url(f'@{build.commit().author}', build.tag_url)
                   for build in self._successful_builds]

        return (f'{TTY.Green}{self.package}{TTY.Reset} {self.v} ' +
                f'{TTY.Blue}[{", ".join(authors)}]{TTY.Reset}')

    def to_md(self) -> str:
        authors = [f'[@{build.commit().author}]({build.tag_url})'
                   for build in self._successful_builds]

        return f'**{self.package}** was updated to **{self.v}** ({", ".join(authors)})'


class Builds:
    _url = 'https://build.getsol.us/builds.json'
    _builds: Optional[List[Build]] = None

    @property
    def all(self) -> List[Build]:
        with request.urlopen(self._url) as data:
            return list(json.load(data, object_hook=lambda d: Build(**d)))

    @property
    def packages(self) -> List[Build]:
        return list({b.pkg: b for b in self.all}.values())

    def updates(self, start: datetime, end: datetime) -> List[Update]:
        updates: Dict[str, Update] = {}

        for build in self._filter(self.all, start, end):
            if build.status != "OK":
                continue

            if build.package in updates:
                updates[build.package].append(build)
            else:
                updates[build.package] = Update(build)

        return list(updates.values())

    def during(self, start: datetime, end: datetime) -> List[Build]:
        return self._filter(self.all, start, end)

    @staticmethod
    def _filter(builds: List[Build], start: datetime, end: datetime) -> List[Build]:
        return list(filter(lambda b: start <= b.date <= end, builds))


@dataclass
class Commit(Listable):
    ref: str
    ts: str
    msg: str
    author: str

    @staticmethod
    def from_line(line: str) -> 'Commit':
        return Commit(*line.split('\x1e'))

    @property
    def date(self) -> datetime:
        return datetime.fromisoformat(self.ts).astimezone(timezone.utc)

    @property
    def package(self) -> str:
        if ':' not in self.msg:
            return '<unknown>'

        return self.msg.split(':', 2)[0].strip()

    @property
    def change(self) -> str:
        if ':' not in self.msg:
            return self.msg.strip()
        return self.msg.split(':', 2)[1].strip()

    @property
    def url(self) -> str:
        return f'https://github.com/getsolus/packages/commit/{self.ref}'

    def to_md(self) -> str:
        return f'[{self.msg}]({self.url})'

    def to_tty(self) -> str:
        return (f'{TTY.Yellow}{TTY.url(self.ref, self.url)}{TTY.Reset} '
                f'{self.date} '
                f'{TTY.Green}{self.package}: {TTY.Reset}{self.change} '
                f'{TTY.Blue}[{self.author}]{TTY.Reset} ' +
                TTY.url('[🡕]', self.url))


class Git:
    _cmd = ['git', '-c', 'color.ui=always', 'log', '--date=iso-strict', '--no-merges',
            '--reverse', '--pretty=format:%h%x1e%ad%x1e%s%x1e%an']

    def commits_by_pkg(self, start: datetime, end: datetime) -> Dict[str, List[Commit]]:
        commits: Dict[str, List[Commit]] = {}
        for commit in self.commits(start, end):
            commits[commit.package] = commits.get(commit.package, []) + [commit]

        return commits

    def commits(self, start: datetime, end: datetime) -> List[Commit]:
        return [Commit.from_line(line) for line in self._commits(start, end)]

    def _commits(self, start: datetime, end: datetime) -> List[str]:
        out = subprocess.Popen(self._cmd + [f'--after={start}', f'--before={end}'],
                               stdout=subprocess.PIPE, stderr=sys.stderr).stdout
        if out is None:
            return []

        return out.read().decode('utf8').strip().split("\n")


def parse_date(date: str) -> datetime:
    out = subprocess.Popen(['date', '-u', '--iso-8601=s', '--date=' + date],
                           stdout=subprocess.PIPE).stdout
    if out is None:
        raise ValueError(f'invalid date: {repr(date)}')

    return datetime.fromisoformat(out.read().decode('utf8').strip())


class Printer:
    def __init__(self, after: str, before: str):
        self.start = parse_date(after)
        self.end = parse_date(before)
        self.builds = Builds()
        self.git = Git()

    def print(self, kind: str, format: str, sort: bool = False) -> None:
        items = self._items(kind)
        if sort:
            items = sorted(items, key=lambda item: (item.package, item.date))

        print(f'{len(items)} {cli_args.command}:')
        self._print(items, format)

    def follow(self, kind: str, format: str) -> None:
        while True:
            self.end = datetime.now(timezone.utc)
            self._print(self._items(kind), format)
            self.start = self.end
            time.sleep(10)

    def _items(self, kind: str) -> Sequence[Listable]:
        match kind:
            case 'builds':
                return self.builds.during(self.start, self.end)
            case 'updates':
                return self.builds.updates(self.start, self.end)
            case 'commits':
                return self.git.commits(self.start, self.end)
            case _:
                raise ValueError(f'unsupported log kind: {kind}')

    @staticmethod
    def _print(items: Sequence[Listable], fmt: str) -> None:
        for item in items:
            Printer._print_item(item, fmt)

    @staticmethod
    def _print_item(item: Listable, fmt: str) -> None:
        match fmt:
            case 'tty':
                print(item.to_tty())
            case 'md':
                print(f'- {item.to_md()}')
            case _:
                raise ValueError(f'unsupported format: {fmt}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, choices=['builds', 'updates', 'commits'])
    parser.add_argument('after', type=str, help='Show builds after this date')
    parser.add_argument('before', type=str, nargs='?', default=datetime.now(timezone.utc).isoformat(),
                        help='Show builds before this date. Defaults to `now`.')
    parser.add_argument('--format', '-f', type=str, choices=['md', 'tty'], default='tty')
    parser.add_argument('--sort', '-s', action='store_true', help='Sort packages in lexically ascending order')
    parser.add_argument('--follow', '-F', action='store_true',
                        help='Wait for and output new entries when they are created')

    cli_args = parser.parse_args()
    printer = Printer(cli_args.after, cli_args.before)

    if cli_args.follow:
        printer.follow(cli_args.command, cli_args.format)
    else:
        printer.print(cli_args.command, cli_args.format, cli_args.sort)
