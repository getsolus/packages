#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import tempfile
import yaml
import time
import json
import base64

from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from xml.etree import ElementTree
from urllib import request
from email.utils import parsedate_to_datetime

sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

from common.CI.package_checks import Git              # noqa: E402
from common.Scripts.worklog import Builds             # noqa: E402
from common.Scripts.worklog import Build as APIBuild  # noqa: E402


def get_yml_tag(spec: str) -> str:
    with open(spec, 'r') as f:
        yml = yaml.safe_load(f)

        return f"{yml['name']}-{yml['version']}-{yml['release']}"


def get_spec_tag(spec: str) -> str:
    root = ElementTree.parse(spec).getroot()
    hist = root.findall('History')
    last_update = hist[0].findall('Update')[0]
    name = root.findall('Source')[0].findall('Name')[0].text
    version = str(last_update.findall('Version')[0].text)
    release = str(last_update.attrib['release'])

    return '%s-%s-%s' % (name, version, release)


@dataclass
class Build:
    source: str
    tag: str
    path: str
    ref: str
    comment: str


class Index:
    INDEX_XZ_URL = 'https://cdn.getsol.us/repo/unstable/eopkg-index.xml.xz'
    INDEX_SHA_URL = 'https://cdn.getsol.us/repo/unstable/eopkg-index.xml.sha256sum'

    def __init__(self) -> None:
        self.refresh()

    def refresh(self) -> datetime:
        self._last_modified, self._sha = self._request(self.INDEX_SHA_URL)

        return self._last_modified

    @staticmethod
    def _request(url: str) -> tuple[datetime, str]:
        with request.urlopen(url) as conn:
            last_modified = parsedate_to_datetime(conn.headers['last-modified'])
            return last_modified, conn.read().decode()


class Publisher:
    def __init__(self, base: Optional[str], head: str, path: str, title: str,
                 push: bool, noop: bool, render: bool, wait: bool):
        self.base = base or 'HEAD'
        self.head = head
        self.title = title
        self.push = push
        self.noop = noop
        self.render = render
        self.wait = wait
        self.git = Git(path)

    def run(self) -> bool:
        commits = self.git.commit_refs(self.base, self.head)
        commits.reverse()

        packages = {commit: self._packages(commit) for commit in commits}
        invalid = {commit: packages for commit, packages in packages.items()
                   if len(packages) != 1 or any(p is None for p in packages)}

        if len(invalid) > 0:
            print('Found commits with an incorrect number of packages:')
            for commit, package_names in invalid.items():
                print(f'Commit {repr(commit)}: {", ".join(package_names) if package_names else "no packages"}')

            return True

        if self.push:
            self._git_push()

        for i, commit in enumerate(commits):
            if self.render:
                self._render(commit)

            comment = f'BUILD {i+1}/{len(commits)}'
            if self.title:
                comment = f'{self.title}\n{comment}'

            id = self._push_build(self._build_for_commit(commit, comment, packages[commit][0]))
            if self.wait:
                self._wait_for_build(id)

        if self.wait:
            self._notify_finished()

        return False

    def _packages(self, commit: str) -> List[str]:
        packages = set([self._package_for_file(f) for f in self.git.files_in_commit(commit)])

        return [package for package in packages if package is not None]

    def _build_for_commit(self, commit: str, comment: str, path: str) -> Build:
        return Build(os.path.basename(path), self._gettag(path), path, commit, comment)

    def _gettag(self, path: str) -> str:
        if os.path.exists(os.path.join(path, 'package.yml')):
            return get_yml_tag(os.path.join(path, 'package.yml'))

        return get_spec_tag(os.path.join(path, 'pspec.xml'))

    @staticmethod
    def _package_for_file(file: str) -> Optional[str]:
        parts = file.split('/')
        if len(parts) < 3 or parts[0] != 'packages':
            return None

        return str(os.path.join(*parts[0:3]))

    def _git_push(self) -> None:
        print('Pushing to Git')
        if not self.noop:
            self.git.run('push')

    def _push_build(self, build: Build) -> int:
        print(f'Pushing build: {build}')
        if self.noop:
            return Builds().all[-1].id

        output = self._run('ssh', 'build-controller@build.getsol.us', 'build',
                           build.source, build.tag, build.path, build.ref,
                           base64.b64encode(build.comment.encode()).decode())

        return int(json.loads(output)['id'])

    def _wait_for_build(self, id: int) -> None:
        print(f'Waiting for build: {id}')

        while True:
            build = next(b for b in Builds().all if b.id == id)
            if build.status == 'OK':
                break

            if build.status == 'FAILED':
                self._notify_failed(build)
                raise Exception(f'Build for {build.package} failed')

            time.sleep(10)

        index = Index()
        while index.refresh() < build.date:
            time.sleep(1)

    def _notify_failed(self, build: APIBuild) -> None:
        self._run('notify-send', '--expire-time=0', '--urgency=critical', '--app-name=Solus Builds',
                  f'Build for {build.tag} failed!')
        self._run('paplay', '/usr/share/sounds/freedesktop/stereo/suspend-error.oga')

    def _notify_finished(self) -> None:
        self._run('notify-send', '--expire-time=0', '--app-name=Solus Builds',
                  'All builds finished!')

    def _render(self, commit: str) -> None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as f:
            res = subprocess.run(['pandoc', '--from=commonmark', '--to=html'], text=True,
                                 input=self.git.commit_message(commit), capture_output=True)
            if res.returncode != 0:
                raise Exception("pandoc error: " + res.stderr)

            f.write(res.stdout.encode('utf-8'))
            f.close()
            self._run('xdg-open', f.name)

    @staticmethod
    def _run(*args: str) -> str:
        res = subprocess.run(args, text=True, capture_output=True)
        if res.returncode != 0:
            raise Exception(f'error executing command: {res.stderr}{res.stdout}')

        return str(res.stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script publishes a series of builds to the build server. "
                    "Run `go-task run-safety-catches` before using this script.")
    parser.add_argument('--base', type=str, default='origin/main',
                        help='Optional reference to the base branch')
    parser.add_argument('--head', type=str, default='HEAD',
                        help='Optional reference to the current branch head')
    parser.add_argument('--root', type=str, default='.',
                        help='Repository root directory')
    parser.add_argument('--title', type=str, default='',
                        help='Title of the build series')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Show what actions would be taken, but do not actually publish any builds')
    parser.add_argument('-s', '--skip-push', action='store_true',
                        help='Skip the Git Push before the builds')
    parser.add_argument('-r', '--render-commits', action='store_true',
                        help='Render the commits and show them in a web browser (requires `pandoc`)')
    parser.add_argument('-w', '--wait', action='store_true',
                        help='Wait for builds to complete before pushing the next one')

    cli_args = parser.parse_args()
    checker = Publisher(cli_args.base, cli_args.head, cli_args.root, cli_args.title,
                        not cli_args.skip_push, cli_args.dry_run, cli_args.render_commits, cli_args.wait)

    exit(checker.run())
