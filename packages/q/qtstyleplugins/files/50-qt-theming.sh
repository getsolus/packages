# Begin /usr/share/defaults/etc/profile.d/50-qt-theming.sh

if [ -z "${QT_QPA_PLATFORMTHEME}" ]; then
    export QT_QPA_PLATFORMTHEME="gtk2"
fi

if [ "${XDG_CURRENT_DESKTOP}" = "KDE" ]; then
    unset QT_QPA_PLATFORMTHEME
fi

# End /usr/share/defaults/etc/profile.d/50-qt-theming.sh
