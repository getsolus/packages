#!/usr/bin/env bash

# Safety catch to prevent system.base/system.devel pkgs where there are additions to abi_used_libs from being publishing accidently.
# Otherwise, if a system.base/system.devel pkg depends on another pkg that isn't in system.base/system.devel the solbuild image will refuse to update.

# FIXME: Check for rundeps changes as well

LAST_COMMIT_DIFF=`git diff @~ @`

if [[ `git grep -E 'system.base|system.devel' package.yml` ]]; then
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

#FILES_PATTERN='abi_used_libs'
#FORBIDDEN='system.base'
#git diff --cached --name-only | \
#    grep -E $FILES_PATTERN | \
#    GREP_COLORS='mt=4;5;37;41' xargs grep --color --with-filename -n $FORBIDDEN && echo 'COMMIT REJECTED Found "$FORBIDDEN" references. Please remove them before commiting' && exit 1
