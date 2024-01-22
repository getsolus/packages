#!/usr/bin/env bash

# Goes to the root directory of the solus packages
# git repository from anywhere on the filesystem.
# This function will only work if this script is sourced
# by your bash shell.
function gotosoluspkgs() {
    cd "$(dirname "$(readlink "${BASH_SOURCE[0]}")")/../../" || return 1
}

# Goes to the root directory of the git repository
function goroot() {
    cd "$(git rev-parse --show-toplevel)" || return 1
}

# Push into a package directory
function gotopkg() {
    cd "$(git rev-parse --show-toplevel)"/packages/*/"$1" || return 1
}

# Re-index the local repo and update eopkg's cache
function localrepo_reindex() {
    sudo eopkg index --skip-signing /var/lib/solbuild/local/ --output /var/lib/solbuild/local/eopkg-index.xml && \
    sudo eopkg update-repo
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
