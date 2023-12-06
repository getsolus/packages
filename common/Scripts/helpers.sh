#!/usr/bin/env bash

# shellcheck wants to add '|| exit 1' willy nilly, so let's
# build a nice 'failmsg' function instead.
function failmsg() {
    echo "$*"
    return 1
}

# Goes to the root directory of the solus packages
# git repository from anywhere on the filesystem.
# This function will only work if this script is sourced
# by your bash shell.
function gotosoluspkgs() {
    cd "$(dirname "$(readlink "${BASH_SOURCE[0]}")")/../../" || \
        failmsg "Unable to find the solus packages git dir."
}

# Goes to the root directory of the git repository
function goroot() {
    local pkgroot="$(git rev-parse --show-toplevel)"
    [[ -n "${pkgroot}" ]] && cd "${pkgroot}" || \
        failmsg "If you're not somewhere in the solus packages git dir, use gotosoluspkgs instead."
}

# Push into a package directory
function gotopkg() {
    local arg="$1"
    gotosoluspkgs
    if [[ -n "$arg" ]]; then
        cd "$(git rev-parse --show-toplevel)"/packages/*/"$arg" || \
            failmsg "Something went wrong."
    else
        failmsg "No package specified, going to the root of the solus packages git dir instead."
    fi
}

# What provides a lib
function whatprovides() {
    gotosoluspkgs
    grep "$1" "$(git rev-parse --show-toplevel)"/packages/*/*/abi_libs
}

# What uses a lib
function whatuses() {
    gotosoluspkgs
    grep "$1" "$(git rev-parse --show-toplevel)"/packages/*/*/abi_used_libs
}


# Bash completions
_gotopkg()
{
    # list of package directories we can go into
    _list=$(ls "$(git rev-parse --show-toplevel)"/packages/*/)

    local cur
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}

    if [[ $COMP_CWORD -eq 1 ]] ; then
        # set up an array with valid package dirname completions
        readarray -t COMPREPLY < <(compgen -W "${_list}" -- "${cur}")
        return 0
    fi
}

complete -F _gotopkg gotopkg
