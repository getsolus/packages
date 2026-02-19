#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from typing import TypedDict


class SubprocessResult(TypedDict):
    stdout: str
    stderr: str
    returncode: int


def validate(path: str, *args: str) -> SubprocessResult:
    if not os.path.isfile(path):
        raise FileNotFoundError("AppStream file not found")

    overrides = {
        "all-categories-ignored": "error",
        "category-invalid": "error",
        "cid-desktopapp-is-not-rdns": "error",
        # "cid-domain-not-lowercase": "info",
        "cid-has-number-prefix": "error",
        "cid-missing-affiliation-gnome": "error",
        "cid-rdns-contains-hyphen": "error",
        # "component-name-too-long": "info",
        "content-rating-missing": "error",
        # "description-has-plaintext-url": "info",
        "desktop-app-launchable-omitted": "error",
        "desktop-file-not-found": "error",
        # "developer-id-invalid": "info",
        "developer-id-missing": "error",
        "invalid-child-tag-name": "error",
        "metainfo-filename-cid-mismatch": "error",
        "metainfo-legacy-path": "error",
        "metainfo-multiple-components": "error",
        "name-has-dot-suffix": "info",
        "releases-info-missing": "error",
        # "summary-too-long": "info",
        "unknown-tag": "error",
        # "app-categories-missing": "info",
    }

    overrides_value = ",".join([f"{k}={v}" for k, v in overrides.items()])

    cmd = subprocess.run(
        ["appstreamcli", "validate", f"--override={overrides_value}", *args, path],
        capture_output=True,
        check=False,
    )

    ret: SubprocessResult = {
        "stdout": cmd.stdout.decode("utf-8"),
        "stderr": cmd.stderr.decode("utf-8"),
        "returncode": cmd.returncode,
    }

    return ret


def main():
    parser = argparse.ArgumentParser(
        description="A script to lint AppStream metainfo files",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )

    parser.add_argument(
        "-h",
        "--help",
        help="Show this help message and exit.",
        action="help",
        default=argparse.SUPPRESS,
    )

    parser.add_argument(
        "path",
        help="Path to an AppStream metainfo file.",
        type=str,
        nargs=1,
    )

    args = parser.parse_args()
    exit_code = 0

    try:
        ret = validate(args.path, "--explain")
        print(ret["stdout"])  # noqa: T201
        print(ret["stderr"])  # noqa: T201
        exit_code = ret["returncode"]
    except Exception as e:
        print(f"Error validating {args.path}: {e}")
        sys.exit(1)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
