#!/usr/bin/env sh
# Launches element-desktop with flags specified in $XDG_CONFIG_HOME/element-desktop-flags.conf

# Make script fail if `cat` fails for some reason
set -e

# Set default value if variable is unset/null
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"

# Attempt to read a config file if it exists
if [ -r "${XDG_CONFIG_HOME}/element-desktop-flags.conf" ]; then
  ELEMENT_DESKTOP_FLAGS="$(cat "$XDG_CONFIG_HOME/element-desktop-flags.conf")"
fi

# Wayland auto-detection. If the session is a wayland session then this will launch as a Wayland window unless the ELEMENT_NO_WAYLAND variable is set
if [ -z "${ELEMENT_NO_WAYLAND+set}" ]; then
  if [ -z "${ELECTRON_OZONE_PLATFORM_HINT+set}" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
  fi
fi

# shellcheck disable=SC2086
exec /usr/share/element/element-desktop $ELEMENT_DESKTOP_FLAGS "$@"
