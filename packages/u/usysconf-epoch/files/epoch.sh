#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="${STATE_DIR:=/var/solus/usr-merge}"
MERGE_FLAG_FILE="${MERGE_FLAG_FILE:=${STATE_DIR}/merge-complete}"

OLD_REPO="https://cdn.getsol.us/repo/shannon/eopkg-index.xml.xz"
NEW_REPO="https://cdn.getsol.us/repo/shannon/eopkg-index.xml.xz"

export LC_ALL=C

declare -A DESKTOP_FLAG_FILES=(
    ["budgie"]="/usr/bin/budgie-desktop"
    ["gnome"]="/usr/bin/gnome-shell"
    ["kde"]="/usr/bin/startplasma-wayland"
    ["xfce"]="/usr/bin/xfce4-session"
    ["mate"]="/usr/bin/mate-about"
)
declare -A DESKTOP_SOFTWARE_CENTRE=(
    ["budgie"]="discover"
    ["gnome"]="gnome-software"
    ["kde"]="discover"
    ["xfce"]="discover"
    ["mate"]="discover"
)
declare -A SC_DESKTOP_FILES=(
    ["discover"]="/usr/share/applications/org.kde.discover.desktop"
    ["gnome-software"]="/usr/share/applications/org.gnome.Software.desktop"
)

function update_repo() {
    local repo=""
    local active=""
    while read -r line
    do
        if [[ "${repo}" == "" ]]
        then
            repo="${line% *}"
            active="${line##"${repo}" }"
            continue
        fi

        url="${line##   }"
        if [[ "${url}" == "${OLD_REPO}" ]]
        then
            echo "Updating repo ${repo} to ${NEW_REPO}"

            eopkg add-repo -y "${repo}" "${NEW_REPO}"

            if [[ "${active}" == "[inactive]" ]]
            then
                eopkg disable-repo "${repo}"
            fi
        fi

        repo=""
    done <<< "$(eopkg list-repo --no-color)"
}

function is_installed() {
    eopkg info --no-color --short "${1}" | grep -P '^\[inst\]' >/dev/null
}

function desktop_name() {
    local field

    if [[ "$2" != "" ]]
    then
        field="^Name\[$2\]="
    else
        field="^Name="
    fi

    local name
    name="$(grep "${field}" "${SC_DESKTOP_FILES[$1]}" | head -n1 || true)"

    echo "${name#*=}"
}

function sc_name() {
    local name

    for lang in "${LANG%.*}" "${LANG%_*}" ""
    do
        name="$(desktop_name "$1" "${lang}")"
        if [[ "${name}" != "" ]]
        then
            echo "${name}"
            return
        fi
    done
}

# Based on StackOverflow post by Fabio A.
# See https://stackoverflow.com/a/49533938
function _notify-send() {
    local user

    for bus in /run/user/*/bus
    do
        user="$(stat -c '%U' "${bus}")"
        sudo -u "${user}" env DBUS_SESSION_BUS_ADDRESS="unix:path=$bus" notify-send "$@"
    done
}

if [[ ! -e "${MERGE_FLAG_FILE}" ]]
then
    echo "Not ready: not usr-merged"
    exit 1
fi

if [[ "$(readlink /usr/bin/eopkg)" != "eopkg.bin" ]]
then
    echo "Not ready: eopkg is not python3"
    exit 1
fi

desktop=""
removed_sc=false

# Install appropriate software centre
for d in "${!DESKTOP_FLAG_FILES[@]}"
do
    if [[ -e "${DESKTOP_FLAG_FILES[$d]}" ]]
    then
        desktop="${d}"
        break
    fi
done

sc_package="${DESKTOP_SOFTWARE_CENTRE[$desktop]}"
echo "Detected desktop: ${desktop}"

if ! is_installed "${sc_package}"
then
    echo "Installing new SC: ${sc_package}"
    eopkg install --yes-all "${DESKTOP_SOFTWARE_CENTRE[$desktop]}"
fi

if is_installed solus-sc
then
   echo "Removing old SC"
   eopkg remove --yes-all solus-sc
   removed_sc=true
fi

echo "Checking repository"
update_repo

echo "Finished! Welcome to the new epoch."
if [[ "${removed_sc}" == "true" ]]
then
    _notify-send --urgency=critical \
                 --icon=software \
                 "Solus Software" \
                 "Software Center is now '$(sc_name "${sc_package}")'" || true
fi
