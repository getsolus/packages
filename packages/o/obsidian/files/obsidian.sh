#!/usr/bin/env sh
# Launches Obsidian with flags specified in $XDG_CONFIG_HOME/obsidian-flags.conf

# Make script fail if `cat` fails for some reason
set -e

# Set default value if variable is unset/null
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"

# Attempt to read a config file if it exists
if [ -r "${XDG_CONFIG_HOME}/obsidian-flags.conf" ]; then
  OBSIDIAN_FLAGS="$(cat "$XDG_CONFIG_HOME/obsidian-flags.conf")"
fi

# Wayland auto-detection. If the session is a wayland session then this will launch as a Wayland window unless the OBSIDIAN_NO_WAYLAND variable is set
if [ -z "${OBSIDIAN_NO_WAYLAND+set}" ]; then
  OBSIDIAN_FLAGS="$OBSIDIAN_FLAGS --ozone-platform-hint=auto --enable-features=WaylandWindowDecorations,WebRTCPipeWireCapturer"
fi

exec /usr/share/obsidian/obsidian $OBSIDIAN_FLAGS "$@"
