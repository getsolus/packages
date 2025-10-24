#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

EPOCH_ENABLE="${EPOCH_ENABLE:=no}"

STATE_DIR="${STATE_DIR:=/var/solus/usr-merge}"
MERGE_FLAG_FILE="${MERGE_FLAG_FILE:=${STATE_DIR}/merge-complete}"

OLD_REPO="https://cdn.getsol.us/repo/shannon/eopkg-index.xml.xz"
NEW_REPO="https://cdn.getsol.us/repo/polaris/eopkg-index.xml.xz"

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

desktop=""
replaced_sc=false
switched_repo=false

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
            switched_repo=true

            if ! eopkg add-repo -y "${repo}" "${NEW_REPO}"
            then
                return 1
            fi

            if [[ "${active}" == "[inactive]" ]]
            then
                eopkg disable-repo "${repo}" || true
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

function wait_network() {
    while ! curl -sL -m 10 https://cdn.getsol.us/repo/polaris/eopkg-index.xml.xz > /dev/null
    do
        echo "Waiting for network"
        sleep 10
    done
}

function wait_login() {
    while true
    do
        for path in /run/user/*
        do
            if [[ "$(basename "$path")" -ge 1000 ]]
            then
                # wait for the login to complete
                sleep 10
                return
            fi
        done

        sleep 10
    done
}

function __notify-send-user() {
    local user="$1"
    local bus="$2"
    shift 2

    sudo -u "${user}" env DBUS_SESSION_BUS_ADDRESS="unix:path=${bus}" notify-send "$@"
}

# Based on StackOverflow post by Fabio A.
# See https://stackoverflow.com/a/49533938
function _notify-send() {
    local user

    for bus in /run/user/*/bus
    do
        user="$(stat -c '%U' "${bus}")"
        __notify-send-user "${user}" "${bus}" "$@"
    done
}

function __notify-send-link-user() {
    local user="$1"
    local bus="$2"
    local link="$3"
    shift 3

    action="$(__notify-send-user "${user}" "${bus}" --action="open=More Info" "$@" || true)"
    if [[ "${action}" == "open" ]]
    then
        sudo -u "${user}" env DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS="unix:path=$bus" xdg-open "${link}"
    fi
}

function _notify-send-link() {
    local user
    local action
    local link="$1"
    shift

    for bus in /run/user/*/bus
    do
        user="$(stat -c '%U' "${bus}")"
        __notify-send-link-user "${user}" "${bus}" "$link" "$@" &
    done

    wait
}

function _systemd-notify() {
    if [[ -n "${NOTIFY_SOCKET+x}" ]]
    then
        systemd-notify "$@"
    fi
}

function _exit() {
    _systemd-notify --ready
    exit "$@"
}

if [[ "${EPOCH_ENABLE}" != "yes" ]]
then
    echo "Not enabled, refusing to transition"
    _exit 0
fi

if [[ ! -e "${MERGE_FLAG_FILE}" ]]
then
    echo "Not ready: not usr-merged"
    _exit 1
fi

if [[ "$(readlink /usr/bin/eopkg)" != "eopkg.bin" ]]
then
    echo "Not ready: eopkg is not python3"
    _exit 1
fi

wait_network

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
    while ! eopkg install --yes-all "${DESKTOP_SOFTWARE_CENTRE[$desktop]}"
    do
        echo "Install failed, will retry."
        sleep 10
    done
    replaced_sc=true
fi

if is_installed solus-sc
then
   echo "Removing old SC"
   eopkg remove --yes-all solus-sc
   replaced_sc=true
fi

echo "Checking repository"
while ! update_repo
do
    echo "Failed to check repository, will retry."
    sleep 10
done

echo "Finished! Welcome to the new epoch."
_systemd-notify --ready

if [[ "${replaced_sc}" == "true" ]] || [[ "${switched_repo}" == "true" ]]
then
    wait_login
fi

if [[ "${replaced_sc}" == "true" ]]
then
    _notify-send --urgency=critical \
                 --icon=software \
                 "Solus Software" \
                 "Software Center is now '$(sc_name "${sc_package}")'" || true
fi

if [[ "${switched_repo}" == "true" ]]
then
    _notify-send-link \
        "https://getsol.us/2025/10/11/a-new-epoch-begins/" \
        --urgency=critical \
        --icon=software \
        "Epoch transition complete" \
        "You have been migrated to the new epoch."
fi
