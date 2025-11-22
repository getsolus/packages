#!/usr/bin/env bash

# Creates a new package from the package name and tarball

set -euo pipefail

if [[ $# -eq 2 ]]; then
    PACKAGE="$1"
    TARBALL="$2"
elif [[ $# -gt 0 && $# -ne 2 ]]; then
    echo "Usage: $0 <package name> <tarball>"
    exit 1
else
    # Loop until a valid package name is entered
    while true; do
        read -p "Package name: " prompt
        if [[ "$prompt" =~ ^[a-z0-9.]+(-[a-z0-9.]+)*$ ]]; then
            PACKAGE="$prompt"
            break
        else
            echo "Invalid package name! Only lowercase letters, numbers, dashes, and dots are allowed."
        fi
    done

    read -p "Tarball URL: " prompt
    TARBALL="${prompt}"
fi

YAUTO=$(git rev-parse --show-toplevel)/common/Scripts/yauto.py

# Basic repo name linting check (for non-interactive calls)
if [[ ! "${PACKAGE}" =~ ^[a-z0-9.]+(-[a-z0-9.]+)*$ ]]; then
    echo "Package names are restricted to US ASCII lowercase letters, numbers, dashes, and, dots."
    exit 1
fi

# FIXME: Don't hardcode this case
if [[ ${PACKAGE:0:2} == "py" ]]; then
    DIR="packages/py/${PACKAGE}"
else
    DIR="packages/${PACKAGE:0:1}/${PACKAGE}"
fi

mkdir -p $(git rev-parse --show-toplevel)/${DIR}

pushd $(git rev-parse --show-toplevel)/${DIR}
$YAUTO ${TARBALL} ${PACKAGE}

printf "\npackage.yml created in ${DIR}\n"
