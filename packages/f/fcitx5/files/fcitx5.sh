if [ ! "$XDG_SESSION_TYPE" = "tty" ]   # if this is a gui session (not tty)
then
    # let's use fcitx instead of fcitx5 to make flatpak happy
    # this may break behavior for users who have installed both
    # fcitx and fcitx5, let then change the file on their own
    export INPUT_METHOD=fcitx
    export GTK_IM_MODULE=fcitx
    export QT_IM_MODULE=fcitx
    export XMODIFIERS=@im=fcitx
fi
