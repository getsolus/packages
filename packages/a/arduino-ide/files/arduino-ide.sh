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

# Wayland auto-detection. If the session is a wayland session then this will launch as a Wayland window unless the ARDUINO_IDE_NO_WAYLAND variable is set
if [ -z "${ARDUINO_IDE_NO_WAYLAND+set}" ]; then
  if [ -z "${ELECTRON_OZONE_PLATFORM_HINT+set}" ]; then
    export ELECTRON_OZONE_PLATFORM_HINT="auto"
  fi
fi

exec /usr/share/arduino-ide/arduino-ide $ARDUINO_IDE_FLAGS $@
