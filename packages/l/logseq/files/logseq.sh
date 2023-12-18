#!/usr/bin/env sh
# Launches Logseq with flags specified in $XDG_CONFIG_HOME/logseq-flags.conf

# Make script fail if `cat` fails for some reason
set -e

# Set default value if variable is unset/null
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"

# Attempt to read a config file if it exists
if [ -r "${XDG_CONFIG_HOME}/logseq-flags.conf" ]; then
  LOGSEQ_FLAGS="$(cat "$XDG_CONFIG_HOME/logseq-flags.conf")"
fi

# Wayland auto-detection. If the session is a wayland session then this will launch as a Wayland window unless the LOGSEQ_NO_WAYLAND variable is set
if [ -z "${LOGSEQ_NO_WAYLAND+set}" ]; then
  LOGSEQ_FLAGS="$LOGSEQ_FLAGS --ozone-platform-hint=auto --enable-features=WaylandWindowDecorations"
fi

# Use system git
if [ -z "${LOCAL_GIT_DIRECTORY+set}" ]; then
  export LOCAL_GIT_DIRECTORY="/usr"
fi

exec /usr/share/logseq/Logseq $LOGSEQ_FLAGS "$@"
