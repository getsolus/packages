# Begin /usr/share/defaults/etc/profile.d/50-dynamic-resize.sh

# Resolves issues with ncurses based apps failing to dynamically resize
# Only needed in bash
if [ -n "$BASH_VERSION" ]; then
    export -n LINES COLUMNS
fi

# End /usr/share/defaults/etc/profile.d/50-dynamic-resize.sh
