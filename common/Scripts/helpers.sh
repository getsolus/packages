#!/usr/bin/env bash

# Goes to the root directory of the solus packages
# git repository from anywhere on the filesystem.
# This function will only work if this script is sourced
# by your bash shell.
function gotosoluspkgs() {
    cd "$(dirname "$(readlink "${BASH_SOURCE[0]}")")/../../" || exit 1
}

# Goes to the root directory of the git repository
function goroot() {
    cd "$(git rev-parse --show-toplevel)" || exit 1
}

# Push into a package directory
function gotopkg() {
    cd "$(git rev-parse --show-toplevel)"/packages/*/"$1" || exit 1
}

# What provides a lib
function whatprovides() {
    grep "$1" "$(git rev-parse --show-toplevel)"/packages/*/*/abi_libs
}

# What uses a lib
function whatuses() {
    grep "$1" "$(git rev-parse --show-toplevel)"/packages/*/*/abi_used_libs
}


# Bash completions
_gotopkg()
{

    _list=$(ls "$(git rev-parse --show-toplevel)"/packages/*/)

    local cur
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}

    if [[ $COMP_CWORD -eq 1 ]] ; then
        readarray -t COMPREPLY < <(compgen -W "${_list}" -- "${cur}")
        return 0
    fi
}

complete -F _gotopkg gotopkg
