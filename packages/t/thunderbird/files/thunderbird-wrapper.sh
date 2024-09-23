#!/usr/bin/env bash

cmdname=`basename $0`

##
## Variables
##
MOZ_ARCH=$(uname -m)
case $MOZ_ARCH in
	x86_64 | s390x | sparc64)
		MOZ_LIB_DIR="/usr/lib64"
		SECONDARY_LIB_DIR="/usr/lib"
		;;
	* )
		MOZ_LIB_DIR="/usr/lib"
		SECONDARY_LIB_DIR="/usr/lib64"
		;;
esac

MOZ_THUNDERBIRD_FILE="thunderbird"

if [ ! -r $MOZ_LIB_DIR/thunderbird/$MOZ_THUNDERBIRD_FILE ]; then
    if [ ! -r $SECONDARY_LIB_DIR/thunderbird/$MOZ_THUNDERBIRD_FILE ]; then
	echo "Error: $MOZ_LIB_DIR/thunderbird/$MOZ_THUNDERBIRD_FILE not found"
	if [ -d $SECONDARY_LIB_DIR ]; then
	    echo "       $SECONDARY_LIB_DIR/thunderbird/$MOZ_THUNDERBIRD_FILE not found"
	fi
	exit 1
    fi
    MOZ_LIB_DIR="$SECONDARY_LIB_DIR"
fi
MOZ_DIST_BIN="$MOZ_LIB_DIR/thunderbird"
MOZ_LANGPACKS_DIR="$MOZ_DIST_BIN/langpacks"
MOZ_EXTENSIONS_PROFILE_DIR="$HOME/.mozilla/extensions/{3550f703-e582-4d05-9a08-453d09bdfdc6}"
MOZ_PROGRAM="$MOZ_DIST_BIN/$MOZ_THUNDERBIRD_FILE"

##
## Wayland is now enabled by default as of Thunderbird 128, but let's still allow users to opt out via MOZ_DISABLE_WAYLAND
## If the user already has MOZ_ENABLE_WAYLAND set don't clobber it
##
if [ $MOZ_DISABLE_WAYLAND ] && [ -z ${MOZ_ENABLE_WAYLAND+x} ]; then
  export MOZ_ENABLE_WAYLAND=0
fi

##
## Use D-Bus remote exclusively when there's Wayland display.
##
if [ "$WAYLAND_DISPLAY" ]; then
  export MOZ_DBUS_REMOTE=1
fi

##
## Set MOZILLA_FIVE_HOME
##
MOZILLA_FIVE_HOME="$MOZ_DIST_BIN"

export MOZILLA_FIVE_HOME

##
## Make sure that we set the plugin path
##
MOZ_PLUGIN_DIR="plugins"

if [ "$MOZ_PLUGIN_PATH" ]
then
  MOZ_PLUGIN_PATH=$MOZ_PLUGIN_PATH:$MOZ_LIB_DIR/mozilla/$MOZ_PLUGIN_DIR:$MOZ_DIST_BIN/$MOZ_PLUGIN_DIR
else
  MOZ_PLUGIN_PATH=$MOZ_LIB_DIR/mozilla/$MOZ_PLUGIN_DIR:$MOZ_DIST_BIN/$MOZ_PLUGIN_DIR
fi
export MOZ_PLUGIN_PATH

##
## Set MOZ_APP_LAUNCHER for gnome-session
##
export MOZ_APP_LAUNCHER="/usr/bin/thunderbird"

##
## Disable the GNOME crash dialog, Moz has it's own
##
GNOME_DISABLE_CRASH_DIALOG=1
export GNOME_DISABLE_CRASH_DIALOG

##
## Automatically installed langpacks are tracked by .solus-langpack-install
## config file.
##
SOLUS_LANGPACK_CONFIG="$MOZ_EXTENSIONS_PROFILE_DIR/.solus-langpack-install"

# MOZ_DISABLE_LANGPACKS disables language packs completely
MOZILLA_DOWN=0
if ! [ $MOZ_DISABLE_LANGPACKS ] || [ $MOZ_DISABLE_LANGPACKS -eq 0 ]; then
    if [ -x $MOZ_DIST_BIN/$MOZ_THUNDERBIRD_FILE ]; then
        # Is thunderbird running?
        /usr/bin/pidof $MOZ_PROGRAM > /dev/null 2>&1
        MOZILLA_DOWN=$?
    fi
fi

# Modify language pack configuration only when thunderbird is not running
# and language packs are not disabled
if [ $MOZILLA_DOWN -ne 0 ]; then

    # Clear already installed langpacks
    mkdir -p $MOZ_EXTENSIONS_PROFILE_DIR
    if [ -f $SOLUS_LANGPACK_CONFIG ]; then
        rm `cat $SOLUS_LANGPACK_CONFIG` > /dev/null 2>&1
        rm $SOLUS_LANGPACK_CONFIG > /dev/null 2>&1
        # remove all empty langpacks dirs while they block installation of langpacks
        rmdir $MOZ_EXTENSIONS_PROFILE_DIR/langpack* > /dev/null 2>&1
    fi

    # Get locale from system
    CURRENT_LOCALE=$LC_ALL
    CURRENT_LOCALE=${CURRENT_LOCALE:-$LC_MESSAGES}
    CURRENT_LOCALE=${CURRENT_LOCALE:-$LANG}

    # Try with a local variant first, then without a local variant
    SHORTMOZLOCALE=`echo $CURRENT_LOCALE | sed "s|_\([^.]*\).*||g" | sed "s|\..*||g"`
    MOZLOCALE=`echo $CURRENT_LOCALE | sed "s|_\([^.]*\).*|-\1|g" | sed "s|\..*||g"`

    function create_langpack_link() {
        local language=$*
        local langpack=langpack-${language}@thunderbird.mozilla.org.xpi
        if [ -f $MOZ_LANGPACKS_DIR/$langpack ]; then
            rm -rf $MOZ_EXTENSIONS_PROFILE_DIR/$langpack
            # If the target file is a symlink (the fallback langpack),
            # install the original file instead of the fallback one
            if [ -h $MOZ_LANGPACKS_DIR/$langpack ]; then
                langpack=`readlink $MOZ_LANGPACKS_DIR/$langpack`
            fi
            ln -s $MOZ_LANGPACKS_DIR/$langpack \
                  $MOZ_EXTENSIONS_PROFILE_DIR/$langpack
            echo $MOZ_EXTENSIONS_PROFILE_DIR/$langpack > $SOLUS_LANGPACK_CONFIG
            return 0
        fi
        return 1
    }

    create_langpack_link $MOZLOCALE || create_langpack_link $SHORTMOZLOCALE || true
fi

# THUNDERBIRD_APP_REMOTINGNAME links Thunderbird with desktop file name
if [ -z "$THUNDERBIRD_APP_REMOTINGNAME" ]
then
  export THUNDERBIRD_APP_REMOTINGNAME=net.thunderbird.Thunderbird
fi
# THUNDERBIRD_DBUS_APP_NAME sets app name for DBus services like Gnome Shell
# search provider or remote launcher
# DBus interface name (or prefix) is org.mozilla.THUNDERBIRD_DBUS_APP_NAME
if [ -z "$THUNDERBIRD_DBUS_APP_NAME" ]
then
  export THUNDERBIRD_DBUS_APP_NAME=thunderbird
fi

# Don't throw "old profile" dialog box.
export MOZ_ALLOW_DOWNGRADE=1

# Run the browser
debugging=0
if [ $debugging = 1 ]
then
  echo $MOZ_PROGRAM "$@"
fi

exec $MOZ_PROGRAM "$@"
