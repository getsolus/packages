#!/usr/bin/env sh
# Launches VSCode with flags specified in $XDG_CONFIG_HOME/vscode-flags.conf

# Make script fail if `cat` fails for some reason
set -e

# Wayland auto-detection. If the session is a wayland session then this will launch as a Wayland window unless the VSCODE_NO_WAYLAND variable is set
if [ -z "${VSCODE_NO_WAYLAND+set}" ]; then
  if [ -z "${ELECTRON_OZONE_PLATFORM_HINT+set}" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
  fi
fi

exec /usr/share/vscode/code-oss $VSCODE_FLAGS "$@"
