#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence
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
        return f'[{self.pkg} {self.version}-{self.release}]({self.tag_url})'

    def to_tty(self) -> str:
        return (f'{TTY.Green}{self.pkg}{TTY.Reset} {self.version}-{self.release} ' +
                f'{TTY.Blue}[{self.builder}]{TTY.Reset} ' +
                TTY.url('[🡕]', self.tag_url))


class Builds:
    _url = 'https://build.getsol.us/builds.json'
    _builds: Optional[List[Build]] = None

    @property
    def all(self) -> List[Build]:
        if self._builds is None:
            with request.urlopen(self._url) as data:
                self._builds = json.load(data, object_hook=lambda d: Build(**d))

        return self._builds

    @property
    def packages(self) -> List[Build]:
        return list({b.pkg: b for b in self.all}.values())

    def during(self, start: datetime, end: datetime) -> List[Build]:
        return self._filter(self.all, start, end)

    def updates(self, start: datetime, end: datetime) -> List[Build]:
        return self._filter(self.packages, start, end)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, choices=['builds', 'updates', 'commits'])
    parser.add_argument('after', type=str, help='Show builds after this date')
    parser.add_argument('before', type=str, help='Show builds before this date')
    parser.add_argument('--format', '-f', type=str, choices=['md', 'tty'], default='tty')

    cli_args = parser.parse_args()
    start = parse_date(cli_args.after)
    end = parse_date(cli_args.before)
    builds = Builds()
    git = Git()
    items: Sequence[Listable] = []

    match cli_args.command:
        case 'builds':
            items = builds.during(start, end)
        case 'updates':
            items = builds.updates(start, end)
        case 'commits':
            items = git.commits(start, end)

    items = sorted(items, key=lambda item: (item.package, item.date))

    match cli_args.format:
        case 'tty':
            lines = [item.to_tty() for item in items]
        case 'md':
            lines = [f'- {item.to_md()}' for item in items]

    print(f'{len(lines)} {cli_args.command}:')
    print("\n".join(lines))
