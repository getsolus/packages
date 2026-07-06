#!/usr/bin/env sh
# Launches Pear Desktop with flags specified in $XDG_CONFIG_HOME/pear-flags.conf

set -e

XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"

if [ -r "${XDG_CONFIG_HOME}/pear-flags.conf" ]; then
    PEAR_FLAGS="$(cat "${XDG_CONFIG_HOME}/pear-flags.conf")"
fi

export ELECTRON_IS_DEV=0

# shellcheck disable=SC2086
exec /usr/share/pear-desktop/youtube-music $PEAR_FLAGS "$@"
