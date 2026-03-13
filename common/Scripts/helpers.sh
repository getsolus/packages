#!/usr/bin/env bash

# Primitive CPE search tool
function cpesearch() {
    function search() {
        curl -s "https://services.nvd.nist.gov/rest/json/cpes/2.0?cpeMatchString=cpe:2.3:*:*:$1*" |\
        jq 'del(.products.[] | select(.cpe.deprecated == true))' | jq -r '.products.[].cpe.cpeName' |\
        cut -d":" -f1-5 | sort -u

        echo -e "\nVerify successful hits by visiting https://cve.circl.lu/search/\$VENDOR/\$PRODUCT"
        echo "- CPE entries for software applications have the form 'cpe:2.3:a:\$VENDOR:\$PRODUCT'"
    }

    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        echo "usage: cpesearch <package-name>"
    elif [[ $# -eq 0 ]]; then
        echo "Warning: No paramaters passed, using current directory name. Pass --help to see usage"
        search "$(basename "$(pwd)")"
    else
        search "$1"
    fi
}

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

function quickfixup() {
    if [[ ! -f "package.yml" ]]; then
        echo "No package.yml found in current directory, aborting!"
        return 1
    fi

    if ! git status --porcelain -- . | grep -q '^ M'; then
        echo "No files in current directory are modified, aborting!"
        return 1
    fi

    # Be explicit about adding files specific to packaging to avoid
    # adding aliens
    local paths=(abi_* package.yml pspec_x86_64.xml monitoring.yaml files/)
    for path in "${paths[@]}"; do
        [[ -e $path ]] && git add "$path"
    done

    # Fixup the last commit in the directory
    git commit --fixup "$(git log -1 --format="%h" -- .)"
    git rebase origin/HEAD --autosquash --autostash

    # Print out the commit for the user
    git log -1 -- .
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
