#!/usr/bin/env python3
import os
import subprocess
import sys

common_dir = os.path.abspath(os.path.realpath(os.path.join(sys.argv[0], '..', '..', '..')))
package_checks = os.path.join(common_dir, 'common', 'CI', 'package_checks.py')


def _run(name: str, *args: str) -> bool:
    res = subprocess.run(args, stdout=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f'{name} failed: {" ".join(args)}')

    return res.returncode == 0


def _git(*args: str) -> str:
    res = subprocess.run(['git'] + list(args), capture_output=True, text=True)
    if res.returncode != 0:
        raise Exception("git error: " + res.stderr)

    return res.stdout.strip()


if __name__ == "__main__":
    files = _git('diff', '--cached', '--name-only', '--diff-filter=ACM').split("\n")

    if not _run('Package checks', package_checks, *files):
        exit(1)
