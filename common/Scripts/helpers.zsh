#!/usr/bin/env zsh

autoload -U +X compinit && compinit
autoload -U +X bashcompinit && bashcompinit

# Goes to the root directory of the solus packages
# git repository from anywhere on the filesystem.
# This function will only work if this script is sourced
# by your zsh shell.
function gotosoluspkgs() {
    SCRIPT_PATH=$functions_source[gotosoluspkgs]
    cd $(dirname $(readlink "${SCRIPT_PATH}"))/../../
}

# Goes to the root directory of the git repository
function goroot() {
    cd $(git rev-parse --show-toplevel)
}

# Change into a package directory
function gotopkg() {
    cd $(git rev-parse --show-toplevel)/packages/*/$1
}

# Re-index the local repo and update eopkg's cache
function localrepo_reindex() {
    sudo eopkg index --skip-signing /var/lib/solbuild/local/ --output /var/lib/solbuild/local/eopkg-index.xml && \
    sudo eopkg update-repo
}

# What provides a lib
function whatprovides() {
    grep $1 $(git rev-parse --show-toplevel)/packages/*/*/abi_libs
}

# What uses a lib
function whatuses() {
    grep $1 $(git rev-parse --show-toplevel)/packages/*/*/abi_used_libs
}

# Package name completion
_gotopkg()
{
    _list=$(ls $(git rev-parse --show-toplevel)/packages/*/)

    local cur prev
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    if [[ $COMP_CWORD -eq 1 ]] ; then
        COMPREPLY=( $(compgen -W "${_list}" -- ${cur}) )
        return 0
    fi
}

complete -F _gotopkg gotopkg

