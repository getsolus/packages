#!/usr/bin/env sh
# Launches Bitwarden with flags specified in $XDG_CONFIG_HOME/bitwarden-flags.conf

# Make script fail if `cat` fails for some reason
set -e

# Set default value if variable is unset/null
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"

# Attempt to read a config file if it exists
if [ -r "${XDG_CONFIG_HOME}/bitwarden-flags.conf" ]; then
  BITWARDEN_FLAGS="$(cat "$XDG_CONFIG_HOME/bitwarden-flags.conf")"
fi

# Wayland auto-detection. If the session is a wayland session then this will launch as a Wayland window unless the BITWARDEN_NO_WAYLAND variable is set
if [ -z "${BITWARDEN_NO_WAYLAND+set}" ]; then
  BITWARDEN_FLAGS="$BITWARDEN_FLAGS --ozone-platform-hint=auto --enable-features=WaylandWindowDecorations"
fi

exec /usr/share/bitwarden-desktop/bitwarden-desktop $BITWARDEN_FLAGS $@
