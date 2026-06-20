#!/usr/bin/env sh
# Launches Zulip with flags specified in $XDG_CONFIG_HOME/zulip-flags.conf

set -e

XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"

if [ -r "${XDG_CONFIG_HOME}/zulip-flags.conf" ]; then
  ZULIP_FLAGS="$(cat "$XDG_CONFIG_HOME/zulip-flags.conf")"
fi

if [ -z "${ZULIP_NO_WAYLAND+set}" ]; then
  if [ -z "${ELECTRON_OZONE_PLATFORM_HINT+set}" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
  fi
fi

# shellcheck disable=SC2086
exec /usr/share/zulip/zulip $ZULIP_FLAGS "$@"
