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

MOZ_FIREFOX_FILE="firefox"

if [ ! -r $MOZ_LIB_DIR/firefox/$MOZ_FIREFOX_FILE ]; then
    if [ ! -r $SECONDARY_LIB_DIR/firefox/$MOZ_FIREFOX_FILE ]; then
	echo "Error: $MOZ_LIB_DIR/firefox/$MOZ_FIREFOX_FILE not found"
	if [ -d $SECONDARY_LIB_DIR ]; then
	    echo "       $SECONDARY_LIB_DIR/firefox/$MOZ_FIREFOX_FILE not found"
	fi
	exit 1
    fi
    MOZ_LIB_DIR="$SECONDARY_LIB_DIR"
fi
MOZ_DIST_BIN="$MOZ_LIB_DIR/firefox"
MOZ_LANGPACKS_DIR="$MOZ_DIST_BIN/langpacks"
MOZ_EXTENSIONS_PROFILE_DIR="$HOME/.mozilla/extensions/{ec8030f7-c20a-464f-9b0e-13a3a9e97384}"
MOZ_PROGRAM="$MOZ_DIST_BIN/$MOZ_FIREFOX_FILE"
MOZ_LAUNCHER="$MOZ_DIST_BIN/run-mozilla.sh"

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
export MOZ_APP_LAUNCHER="/usr/bin/firefox"

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
    if [ -x $MOZ_DIST_BIN/$MOZ_FIREFOX_FILE ]; then
        # Is firefox running?
        /usr/bin/pidof $MOZ_PROGRAM > /dev/null 2>&1
        MOZILLA_DOWN=$?
    fi
fi

# Modify language pack configuration only when firefox is not running
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
        local langpack=langpack-${language}@firefox.mozilla.org.xpi
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

# Prepare command line arguments
script_args=""
pass_arg_count=0
while [ $# -gt $pass_arg_count ]
do
  case "$1" in
    -g | --debug)
      script_args="$script_args -g"
      debugging=1
      shift
      ;;
    -d | --debugger)
      if [ $# -gt 1 ]; then
        script_args="$script_args -d $2"
        shift 2
      else
        shift
      fi
      ;;
    *)
      # Move the unrecognized argument to the end of the list.
      arg="$1"
      shift
      set -- "$@" "$arg"
      pass_arg_count=`expr $pass_arg_count + 1`
      ;;
  esac
done

# Don't throw "old profile" dialog box.
export MOZ_ALLOW_DOWNGRADE=1

# Run the browser
debugging=0
if [ $debugging = 1 ]
then
  echo $MOZ_LAUNCHER $script_args $MOZ_PROGRAM "$@"
fi

exec $MOZ_LAUNCHER $script_args $MOZ_PROGRAM "$@"
