# Begin /usr/share/defaults/etc/profile.d/50-qt-theming.sh

if [ -z "${QT_QPA_PLATFORMTHEME}" ]; then
    export QT_QPA_PLATFORMTHEME="gtk2"
fi

# End /usr/share/defaults/etc/profile.d/50-qt-theming.sh
