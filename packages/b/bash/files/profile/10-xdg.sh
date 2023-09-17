# Begin /usr/share/defaults/etc/profile.d/10-xdg.sh

export XDG_DATA_DIRS="/usr/share"
export XDG_CONFIG_DIRS="/usr/share/xdg:/etc/xdg:/usr/share"

if [ -e "/etc/locale.conf" ]; then
    . /etc/locale.conf
fi

export LANG LANGUAGE LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT LC_IDENTIFICATION

# End /usr/share/defaults/etc/profile.d/10-xdg.sh
