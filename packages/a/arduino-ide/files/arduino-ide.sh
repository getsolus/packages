#!/usr/bin/env sh
# Launches Arduino-ide with flags specified in $XDG_CONFIG_HOME/arduino-ide-flags.conf

# Make script fail if `cat` fails for some reason
set -e

# Set default value if variable is unset/null
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"

# Attempt to read a config file if it exists
if [ -r "${XDG_CONFIG_HOME}/arduino-ide-flags.conf" ]; then
  ARDUINO_IDE_FLAGS="$(cat "$XDG_CONFIG_HOME/arduino-ide-flags.conf")"
fi

if [ $XDG_SESSION_TYPE = "wayland" ] && [ -c /dev/nvidia0 ]; then
  ARDUINO_IDE_FLAGS="$ARDUINO_IDE_FLAGS --disable-gpu-sandbox"
fi

exec /usr/share/arduino-ide/arduino-ide $ARDUINO_IDE_FLAGS $@
