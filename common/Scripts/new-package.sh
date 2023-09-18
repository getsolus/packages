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
    read -p "Package name: " prompt
    PACKAGE=${prompt}
    read -p "Tarball URL: " prompt
    TARBALL=${prompt}
fi

# Basic repo name linting check
if [[ ! "${PACKAGE}" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    echo "Package names are restricted to US ASCII lowercase letters, numbers and dashes."
    exit 1
fi

# FIXME: Don't hardcode this case
if [[ ${PACKAGE:0:2} == "py" ]]; then
    DIR="packages/py/${PACKAGE}"
else
    DIR="packages/${PACKAGE:0:1}/${PACKAGE}"
fi

mkdir -p ${DIR}

pushd ${DIR}
../../../common/Scripts/yauto.py ${TARBALL}

printf "\npackage.yml created in ${DIR}\n"
