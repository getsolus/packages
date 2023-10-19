#!/usr/bin/env python3
import argparse
import os

scope_help = "# Scope and title, eg: nano: Update to 1.2.3\n"
help_msg = """

**Summary**
# Describe or link the changes here, for example:
#   - Resolves a bug
# You may also link to a changelog, for example:
#   Release notes can be found [here](https://example.com).


# Uncomment and fill in the following if this update includes security fixes:
# **Security**
# Includes fixes for:
# - CVE-
"""


def commit_scope(commit_dir: str) -> str:
    if os.path.exists(os.path.join(commit_dir, 'package.yml')):
        return os.path.basename(commit_dir) + ': '

    return ''


def template(commit_dir: str, contents: str) -> str:
    return scope_help + commit_scope(commit_dir) + help_msg


def current_message(file: str) -> str:
    with open(file, 'r') as f:
        return f.read()


def render_template(file: str, commit_dir: str) -> None:
    contents = current_message(file)

    with open(file, 'w') as f:
        f.write(template(commit_dir, contents))
        f.write(contents)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str,
                        help='File containing the commit log message')
    parser.add_argument('source', type=str, nargs='?',
                        help='Source of the commit message')
    parser.add_argument('object', type=str, nargs='?',
                        help='Object name, if a `-c`, `-C` or `--amend` was given')
    args = parser.parse_args()
    pwd = os.getenv('PWD') or '/'

    match args.source:
        case 'message' | 'template' | 'merge' | 'squash' | 'commit':
            pass
        case _:
            render_template(args.file, pwd)
