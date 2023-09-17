# Begin /usr/share/defaults/etc/profile.d/50-qt-theming.sh

if [ -z "${QT_QPA_PLATFORMTHEME}" ] && [ "${XDG_CURRENT_DESKTOP}" != "KDE" ]; then
    export QT_QPA_PLATFORMTHEME="gtk2"
    # Let GTK sort the scaling
    export QT_AUTO_SCREEN_SCALE_FACTOR=0
fi

# End /usr/share/defaults/etc/profile.d/50-qt-theming.sh
