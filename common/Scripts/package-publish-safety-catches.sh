#!/usr/bin/env bash

# Safety catches when publishing packages. Not foolproof and there are edge cases where we don't want it which allows for force-pushing.
# Currently:
    # - Checks that the release has been bumped.
    # - Warns if there are additions to abi_used_libs for system.{base,devel} packages.

# FIXME: Check for rundeps changes as well for system.{base,devel} packages.
# FIXME: For the initial inclusion check that the release == 1

LAST_COMMIT_DIFF=`git diff @~ @`

PKG_BUMP=`git diff @~ @ package.yml | grep -w +release`

# Check the release has been bumped
if [[ $PKG_BUMP == "" ]]; then
    echo "Warning: Cannot determine that the release has been bumped"
    read -p "Press y to force-through. If unsure press any other key to abort." prompt
    if [[ $prompt = "y" ]]; then
        exit 0
    else
        exit 1
    fi
fi

# Checks for additions to abi_used_libs for system.{base,devel} packages.

if [[ `git grep -E 'system.base|system.devel' pspec_x86_64.xml` ]]; then
    SYSTEM_BASE_DEVEL_PKG=1
fi

if [[ `grep -E abi_used_libs <<< $LAST_COMMIT_DIFF` ]]; then
    # Only if the change is an addition
    ABI_ADDITION=`git diff @~ @ -U0 --word-diff abi_used_libs | grep {+`
    if [[ $ABI_ADDITION != "" ]]; then
        CHANGED_ABI_USED_LIBS=1
    fi
fi

if [[ ! -z "${SYSTEM_BASE_DEVEL_PKG}" && ! -z "${CHANGED_ABI_USED_LIBS}" ]]; then
    echo "Found a system.base/system.devel pkg where" $ABI_ADDITION "has been added to abi_used_libs."
    echo "Please ensure that the package containing" $ABI_ADDITION "is in system.base/system.devel BEFORE continuing."
    read -p "Press y to continue. If unsure press any other key to abort." prompt
    if [[ $prompt = "y" ]]; then
        exit 0
    else
        exit 1
    fi
fi
