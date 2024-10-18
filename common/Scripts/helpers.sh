#!/usr/bin/env bash

BOLD='\033[1m'
RED='\033[0;31m'
RESET='\033[0m'
YELLOW='\033[0;33m'
GREEN="\033[32m"

# Primitive CPE search tool
function cpesearch() {
    function search() {
        curl -s -X POST https://cpe-guesser.cve-search.org/search -d "{\"query\": [\"$1\"]}" | jq .

        echo "Verify successful hits by visiting https://cve.circl.lu/search/\$VENDOR/\$PRODUCT"
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

function check_update() {
    if [ ! -e "monitoring.yml" ]; then
        echo -e "${RED}monitoring.yml file doesn't exist"
        return 1
    fi
    if [ ! -e "package.yml" ]; then
        echo -e "${RED}package.yml file doesn't exist"
        return 1
    fi

    # Check requirements before starting
    REQUIREMENTS="curl yq jq"
    for i in $REQUIREMENTS; do
        if ! which $i &> /dev/null; then
            echo "Missing requirement: $i. Install it to continue."
            return 1
        fi
    done

    current_version=$(yq '.version' package.yml)
    new_version=$(curl -s -H "Accept: application/json" https://release-monitoring.org/api/v2/versions/?project_id=`yq '.releases.id' monitoring.yml` | jq -r '.stable_versions[:1]' | jq -c '.[]')

    # Strip any quotes and replace underscores with dots
    new_version=${new_version//\"/}
    new_version=${new_version//\'/}
    new_version=${new_version//_/.}
    current_version=${current_version//\"/}
    current_version=${current_version//\'/}

    echo "current version: ${current_version}"
    if [ "$current_version" != "$new_version" ]; then
        echo -e "${YELLOW}lastest version: ${new_version}${RESET}"
        echo -e "${BOLD}Update available${RESET}"
    elif [ "$current_version" == "$new_version" ]; then
        echo -e "${GREEN}lastest version: ${new_version}${RESET}"
        echo "Already using latest version"
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
