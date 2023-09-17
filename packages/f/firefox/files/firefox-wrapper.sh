#!/usr/bin/env bash

##
## Enable Wayland backend?
##
if ! [ $MOZ_DISABLE_WAYLAND ] && [ "$WAYLAND_DISPLAY" ]; then
  if [ "$XDG_CURRENT_DESKTOP" == "GNOME" ]; then
    export MOZ_ENABLE_WAYLAND=1
  fi
##  Enable Wayland on KDE/Sway
##
  if [ "$XDG_SESSION_TYPE" == "wayland" ]; then
    export MOZ_ENABLE_WAYLAND=1
  fi
fi

##
## Use D-Bus remote exclusively when there's Wayland display.
##
if [ "$WAYLAND_DISPLAY" ]; then
  export MOZ_DBUS_REMOTE=1
fi

# Don't throw "old profile" dialog box.
export MOZ_ALLOW_DOWNGRADE=1

exec /usr/lib/firefox/firefox "$@"
