#!/usr/bin/env python3

from datetime import datetime
import hashlib
import requests


GITHUB_API = 'https://api.github.com/repos/mozilla-firefox/firefox'
GITHUB_RAW = 'https://raw.githubusercontent.com/mozilla-firefox/firefox'
CERTDATA_PATH = 'security/nss/lib/ckfw/builtins/certdata.txt'


def last_commit() -> tuple[str, datetime]:
    data = requests.get(GITHUB_API + '/commits', params={
        'path': CERTDATA_PATH,
        'per_page': 1,
    }).json()

    return data[0]['sha'], datetime.fromisoformat(data[0]['commit']['author']['date'])


def certdata_url(ref: str) -> str:
    return f'{GITHUB_RAW}/{ref}/{CERTDATA_PATH}'


def shasum(url: str) -> str:
    return hashlib.sha256(requests.get(url, stream=True, allow_redirects=True).content).hexdigest()


if __name__ == "__main__":
    ref, date = last_commit()
    version = date.strftime('%Y%m%d')
    url = certdata_url(ref)
    sha = shasum(url)

    with open('package.yml') as f:
        lines = [line.rstrip() for line in f.readlines()]

    release = int(lines[2].split(" ")[-1]) + 1
    lines[1] = f"version    : '{version}'"
    lines[2] = f"release    : {release}"
    lines[5] = f"    - {url} : {sha}"

    with open('package.yml', 'w') as f:
        f.truncate()
        f.write("\n".join(lines) + "\n")
