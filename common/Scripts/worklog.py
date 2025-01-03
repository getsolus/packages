#!/usr/bin/env python3
import argparse
import html
import json
import os.path
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set
from urllib import request


class TTY:
    Reset = '\033[0m'
    Red = '\033[31m'
    Green = '\033[32m'
    Yellow = '\033[33m'
    Blue = '\033[34m'
    White = '\033[97m'
    DarkGrey = '\033[1;30m'

    @staticmethod
    def color(color: str, text: str) -> str:
        return color + text + TTY.Reset

    @staticmethod
    def url(name: str, ref: str, alt: Optional[str] = None) -> str:
        if alt is None:
            alt = name

        if TTY.legacy():
            return alt

        return f'\033]8;;{ref}\033\\{name}\033]8;;\033\\'

    @staticmethod
    def legacy() -> bool:
        return os.environ.get("TERM") == "linux"


@dataclass
class Symbol:
    """
    Symbol represents a symbol for a terminal.
    It can have both a modern (eg: Emoji) and legacy (CP-437) representation.
    """
    modern: str
    legacy: str

    def __str__(self) -> str:
        if TTY.legacy():
            return self.legacy

        return self.modern


class Symbols:
    """
    Symbols is a symbol table defining named for both modern and legacy terminals.
    """
    link = Symbol('[🡕]', '[^]')
    unclaimed = Symbol('⏳', '│∙│')
    building = Symbol('🔄', '│»│')
    ok = Symbol('✅', '│√│')
    failed = Symbol('❌', '│x│')


class Listable:
    @property
    def package(self) -> str:
        raise NotImplementedError

    @property
    def date(self) -> datetime:
        raise NotImplementedError

    def to_md(self) -> str:
        raise NotImplementedError

    def to_html(self) -> str:
        raise NotImplementedError

    def to_tty(self) -> str:
        raise NotImplementedError


class GitHubObject:
    @staticmethod
    def get(name: str, api_path: str) -> Dict[str, Any]:
        cached = GitHubObject.__get_cache(name)
        if cached is not None:
            return cached

        return GitHubObject.__get_gh_cli(name, api_path)

    @staticmethod
    def __get_cache(name: str) -> Optional[Dict[str, Any]]:
        file = GitHubObject.__tempfile(name)
        if not os.path.exists(file):
            return None

        with open(file, 'rb') as f:
            return json.loads(f.read())  # type: ignore

    @staticmethod
    def store_cache(name: str, commit: str) -> None:
        with open(os.path.join(GitHubObject.__tempfile(name)), 'w') as fh:
            fh.write(commit)

    @staticmethod
    def __tempfile(name: str) -> str:
        dir = os.path.join(tempfile.gettempdir(), '_solus_worklog')
        os.makedirs(dir, exist_ok=True, mode=0o700)

        return os.path.join(dir, name + '.json')

    @staticmethod
    def __get_gh_cli(name: str, path: str) -> Dict[str, Any]:
        res = subprocess.run(['gh', 'api', path],
                             capture_output=True, text=True)
        if res.returncode != 0:
            raise ValueError(f'GitHub API returned non-zero exit: {res.stderr}')

        GitHubObject.store_cache(name, res.stdout)

        return json.loads(res.stdout)  # type: ignore


class GitHubCommit:
    @staticmethod
    def get(ref: str) -> 'GitHubCommit':
        return GitHubCommit(GitHubObject.get(ref, f'repos/getsolus/packages/commits/{ref}'))

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def author(self) -> str:
        author = self._data.get('author')
        if author is not None:
            return str(author.get('login', 'Unknown'))

        return str(self._data['commit']['author']['name'])

    @property
    def message(self) -> str:
        return str(self._data['commit']['message'])

    @property
    def cves(self) -> Set[str]:
        return {m for m in re.findall(r'CVE-\d{4}-\d{4,7}', self.message)}

    @property
    def ghsas(self) -> Set[str]:
        return {m[0] for m in re.findall(r'(GHSA(-[23456789cfghjmpqrvwx]{4}){3})', self.message)}


class GitHubPR(Listable):
    @staticmethod
    def get(id: int) -> 'GitHubPR':
        return GitHubPR(GitHubObject.get(f'pr_{id}', f'repos/getsolus/packages/pulls/{id}'))

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def package(self) -> str:
        if ':' not in self.title:
            return '<unknown>'

        return self.title.split(':', 2)[0].strip()

    @property
    def title(self) -> str:
        return self._data['title']  # type: ignore

    @property
    def date(self) -> datetime:
        return datetime.fromisoformat(self._data['merged_at'])

    @property
    def body(self) -> str:
        return str(self._data['body'])

    @property
    def summary(self) -> str:
        start = self.body.find('**Summary**')
        end = self.body.find('**Test Plan**')

        if start < 0:
            return self.body

        return self.body[start + 11:end].strip()

    @property
    def labels(self) -> list[str]:
        return [label['name'] for label in self._data['labels']]

    @property
    def include_in_sync_notes(self) -> bool:
        return 'Topic: Sync Notes' in self.labels

    def to_md(self) -> str:
        return f'[{self._list_title()}]({self._url})\n{self._prefix_summary()}\n'

    def to_html(self) -> str:
        return f'<a href="{html.escape(self._url, quote=True)}">{html.escape(self._list_title())}</a>' \
              f'<blockquote>{self._html_summary()}</blockquote>'

    def to_tty(self) -> str:
        return f'{TTY.url(self._list_title(), self._url)}\n{self._prefix_summary()}\n'

    def _list_title(self) -> str:
        return self.package if self.package != '<unknown>' else self.title

    def _prefix_summary(self, prefix: str = '  >') -> str:
        return "\n".join([f'{prefix} {line}' for line in self.summary.splitlines()])

    @property
    def _url(self) -> str:
        return self._data['_links']['html']['href']  # type: ignore

    def _html_summary(self) -> str:
        import markdown
        return markdown.markdown(self.summary)


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
    created: Optional[str]
    started: Optional[str]
    finished: Optional[str]
    comment: Optional[str]

    __status_colors = {
        'UNCLAIMED': TTY.DarkGrey,
        'CLAIMED': TTY.Blue,
        'BUILDING': TTY.Blue,
        'OK': TTY.Green,
        'FAILED': TTY.Red,
    }
    __status_symbols = {
        'UNCLAIMED': Symbols.unclaimed,
        'CLAIMED': Symbols.building,
        'BUILDING': Symbols.building,
        'OK': Symbols.ok,
        'FAILED': Symbols.failed,
    }

    @property
    def package(self) -> str:
        return self.pkg

    @property
    def date(self) -> datetime:
        return (self._finished or
                self._started or
                self._created or
                datetime.now(tz=timezone.utc))

    def to_md(self) -> str:
        return f'[{self.pkg} {self.v}]({self.tag_url})'

    def to_html(self) -> str:
        return (f'<a href="{html.escape(self.tag_url, quote=True)}">'
                f'{html.escape(self.pkg)}&nbsp;{html.escape(self.v)}'
                '</a>')

    def to_tty(self) -> str:
        duration = f'({self.duration}) ' if self.duration else ''
        comment = f' # {self._comment}' if self.comment else ''

        return (TTY.color(self.status_color, f'{self.status_symbol} {self.package} ') +
                f'{self.v} ' +
                TTY.color(TTY.Blue, f'[{self.builder}] ') +
                duration +
                TTY.url(str(Symbols.link), self.tag_url, alt='') +
                TTY.color(TTY.DarkGrey, comment))

    @property
    def v(self) -> str:
        return f'{self.version}-{self.release}'

    def commit(self) -> GitHubCommit:
        return GitHubCommit.get(self.ref)

    @staticmethod
    def __parse_date(date: Optional[str]) -> Optional[datetime]:
        if date is None:
            return None

        return datetime.fromisoformat(date).astimezone(timezone.utc)

    @property
    def _created(self) -> Optional[datetime]:
        return self.__parse_date(self.created)

    @property
    def _started(self) -> Optional[datetime]:
        return self.__parse_date(self.started)

    @property
    def _finished(self) -> Optional[datetime]:
        return self.__parse_date(self.finished)

    @property
    def duration(self) -> Optional[str]:
        if self._started is None or self._finished is None:
            return None

        return f'{round((self._finished - self._started).total_seconds())} s'

    @property
    def _comment(self) -> Optional[str]:
        return self.comment.replace('\n', '; ') if self.comment else None

    @property
    def status_color(self) -> str:
        if self.status in self.__status_colors:
            return self.__status_colors[self.status]

        raise ValueError(f'unknown status: {self.status}')

    @property
    def status_symbol(self) -> Symbol:
        if self.status in self.__status_symbols:
            return self.__status_symbols[self.status]

        raise ValueError(f'unknown status: {self.status}')


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

    @property
    def cves(self) -> Set[str]:
        return {cve for build in self._successful_builds
                for cve in build.commit().cves}

    @property
    def ghsas(self) -> Set[str]:
        return {ghsa for build in self._successful_builds
                for ghsa in build.commit().ghsas}

    def to_tty(self) -> str:
        authors = [TTY.url(f'@{build.commit().author}', build.tag_url)
                   for build in self._successful_builds]
        cves = [TTY.url(cve, f'https://nvd.nist.gov/vuln/detail/{cve}')
                for cve in self.cves]
        ghsas = [TTY.url(ghsa, f'https://github.com/advisories/{ghsa}')
                 for ghsa in self.ghsas]
        vulns = sorted(cves + ghsas)

        line = (f'{TTY.Green}{self.package}{TTY.Reset} {self.v} ' +
                f'{TTY.Blue}[{", ".join(authors)}]{TTY.Reset}')

        if len(vulns) > 0:
            line += f' {TTY.Red}[{", ".join(vulns)}]{TTY.Reset}'

        return line

    def to_md(self) -> str:
        authors = [f'[@{build.commit().author}]({build.tag_url})'
                   for build in self._successful_builds]
        cves = [f'[{cve}](https://nvd.nist.gov/vuln/detail/{cve})'
                for cve in self.cves]
        ghsas = [f'[{ghsa}](https://github.com/advisories/{ghsa})'
                 for ghsa in self.ghsas]
        vulns = cves + ghsas

        line = f'**{self.package}** was updated to **{self.v}** ({", ".join(authors)}).'

        if len(vulns) > 0:
            line += f' Includes security fixes for {", ".join(vulns)}.'

        return line

    def to_html(self) -> str:
        authors = [f'<a href="{html.escape(build.tag_url, quote=True)}">@{html.escape(build.commit().author)}</a>'
                   for build in self._successful_builds]
        cves = [f'<a href="https://nvd.nist.gov/vuln/detail/{cve}">{cve}</a>'
                for cve in self.cves]
        ghsas = [f'<a href="https://github.com/advisories/{ghsa}">{ghsa}</a>'
                 for ghsa in self.ghsas]
        vulns = cves + ghsas

        line = (f'<strong>{html.escape(self.package)}</strong> was updated to <strong>{html.escape(self.v)}</strong> '
                f'({", ".join(authors)}).')

        if len(vulns) > 0:
            line += f' Includes security fixes for {", ".join(vulns)}.'

        return line


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

    def updates(self, start: datetime, end: datetime, security: bool = False) -> List[Update]:
        updates: Dict[str, Update] = {}

        for build in self._filter(self.all, start, end):
            if build.package in updates:
                updates[build.package].append(build)
            else:
                updates[build.package] = Update(build)

        if security:
            updates = {pkg: update for pkg, update in updates.items()
                       if len(update.cves) > 0 or len(update.ghsas) > 0}

        return list(updates.values())

    def during(self, start: datetime, end: datetime) -> List[Build]:
        return self._filter(self.all, start, end)

    @staticmethod
    def _filter(builds: List[Build], start: datetime, end: datetime) -> List[Build]:
        return list(filter(lambda b: start < b.date <= end, builds))


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

    @property
    def is_pr(self) -> bool:
        return self.pr is not None

    @property
    def pr(self) -> Optional[GitHubPR]:
        match = re.search(r'\(#(\d+)\)$', self.msg.splitlines()[0])
        if not match:
            return None

        return GitHubPR.get(int(match.group(1)))

    def to_md(self) -> str:
        return f'[{self.msg}]({self.url})'

    def to_html(self) -> str:
        return f'<a href="{html.escape(self.url, quote=True)}">{html.escape(self.msg)}</a>'

    def to_tty(self) -> str:
        return (f'{TTY.Yellow}{TTY.url(self.ref, self.url)}{TTY.Reset} '
                f'{self.date} '
                f'{TTY.Green}{self.package}: {TTY.Reset}{self.change} '
                f'{TTY.Blue}[{self.author}]{TTY.Reset} ' +
                TTY.url(str(Symbols.link), self.url, alt=''))


class Git:
    _cmd = ['git', '-c', 'color.ui=always', 'log', '--date=iso-strict',
            '--reverse', '--pretty=format:%h%x1e%ad%x1e%s%x1e%an']

    def commits_by_pkg(self, start: datetime, end: datetime) -> Dict[str, List[Commit]]:
        commits: Dict[str, List[Commit]] = {}
        for commit in self.commits(start, end):
            commits[commit.package] = commits.get(commit.package, []) + [commit]

        return commits

    def commits(self, start: datetime, end: datetime, merges: bool = False) -> List[Commit]:
        return [Commit.from_line(line) for line in self._commits(start, end, merges)]

    def prs(self, start: datetime, end: datetime) -> List[GitHubPR]:
        return [commit.pr for commit in self.commits(start, end, True)
                if commit.pr is not None]

    def _commits(self, start: datetime, end: datetime, merges: bool) -> List[str]:
        cmd = self._cmd.copy()

        if not merges:
            cmd.append('--no-merges')

        out = subprocess.Popen(cmd + [f'--after={start.isoformat()}', f'--before={end.isoformat()}'],
                               stdout=subprocess.PIPE, stderr=sys.stderr).stdout
        if out is None:
            return []

        lines = out.read().decode('utf8').strip().split("\n")
        if lines == ['']:
            return []

        return lines


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

        if format == 'html':
            print(f'<p>{len(items)} {cli_args.command}:</p>\n<ul>')
        else:
            print(f'{len(items)} {cli_args.command}:')

        self._print(items, format)

        if format == 'html':
            print('</ul>')

    def follow(self, kind: str, format: str) -> None:
        while True:
            self.end = datetime.now(timezone.utc)
            items = self._items(kind)

            self._print(items, format)

            if len(items) > 0:
                self.start = max([i.date for i in items])

            time.sleep(10)

    def _items(self, kind: str) -> Sequence[Listable]:
        match kind:
            case 'builds':
                return self.builds.during(self.start, self.end)
            case 'updates':
                return self.builds.updates(self.start, self.end)
            case 'security-updates':
                return self.builds.updates(self.start, self.end, security=True)
            case 'commits':
                return self.git.commits(self.start, self.end)
            case 'highlights':
                return [pr for pr in self.git.prs(self.start, self.end)
                        if pr.include_in_sync_notes]
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
            case 'html':
                print(f'<li>{item.to_html()}</li>')
            case _:
                raise ValueError(f'unsupported format: {fmt}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            '''
            examples:
              List builds from the last week:
                ./worklog.py builds '1 week ago' now

              Follow builds from the build server as they happen:
                ./worklog.py builds now --follow

              List builds between 8:00 and 18:00 hours local time:
                ./worklog.py builds 8:00 18:00

              List builds between two ISO 8601 formatted dates in UTC:
                ./worklog.py builds 2024-02-21T00:00:00Z 2024-02-28T00:00:00Z

              Create a sorted list of package updates since the last sync in Markdown:
                ./worklog.py updates 2024-03-14T02:08:07Z --sort --format=md

              List commits to the packages repository in the last 24 hours:
                ./worklog.py commits '1 days ago'
            '''
        ))
    parser.add_argument('command', type=str,
                        choices=['builds', 'updates', 'security-updates', 'commits', 'highlights'],
                        help='Type of output to show. '
                             '`builds` shows the builds as produced by the build server, '
                             '`updates` shows per-package updates based on the build server log and GitHub metadata, '
                             '`security-updates` shows updates with security fixes, '
                             '`commits` shows the commits from your local copy of the `packages` repository, '
                             '`highlights` shows the flagged PR summaries from your local `packages` repository.')
    parser.add_argument('after', type=str,
                        help='Show builds after this date. '
                             'The date can be specified in any format parsed by the `date` command.')
    parser.add_argument('before', type=str, nargs='?', default=datetime.now(timezone.utc).isoformat(),
                        help='Show builds before this date. '
                             'The date can be specified in any format parsed by the `date` command. '
                             'Defaults to `now`.')
    parser.add_argument('--format', '-f', type=str, choices=['md', 'tty', 'html'], default='tty',
                        help='Output format: Terminal (`tty`), Markdown (`md`) or HTML (`html`). '
                             'Defaults to `tty`.')
    parser.add_argument('--sort', '-s', action='store_true',
                        help='Sort packages in lexically ascending order.')
    parser.add_argument('--follow', '-F', action='store_true',
                        help='Wait for and output new entries when they are created.')

    cli_args = parser.parse_args()
    printer = Printer(cli_args.after, cli_args.before)

    if cli_args.follow:
        printer.follow(cli_args.command, cli_args.format)
    else:
        printer.print(cli_args.command, cli_args.format, cli_args.sort)
