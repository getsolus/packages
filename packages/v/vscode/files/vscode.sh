#!/usr/bin/env sh
# Launches VSCode with flags specified in $XDG_CONFIG_HOME/vscode-flags.conf

# Make script fail if `cat` fails for some reason
set -e

# Set default value if variable is unset/null
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"

# Attempt to read a config file if it exists
if [ -r "${XDG_CONFIG_HOME}/vscode-flags.conf" ]; then
  VSCODE_FLAGS="$(cat "$XDG_CONFIG_HOME/vscode-flags.conf")"
fi

# Wayland auto-detection. If the session is a wayland session then this will launch as a Wayland window unless the VSCODE_NO_WAYLAND variable is set
if [ -z "${VSCODE_NO_WAYLAND+set}" ]; then
  VSCODE_FLAGS="$VSCODE_FLAGS --ozone-platform-hint=auto --enable-features=WaylandWindowDecorations"
fi

exec /usr/share/vscode/code-oss $VSCODE_FLAGS "$@"
