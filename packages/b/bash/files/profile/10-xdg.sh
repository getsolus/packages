# Begin /usr/share/defaults/etc/profile.d/10-xdg.sh

export XDG_DATA_DIRS="${XDG_DATA_DIRS:-/usr/local/share/:/usr/share/}"
export XDG_CONFIG_DIRS="${XDG_CONFIG_DIRS:-/run/xdg/:/etc/xdg/:/usr/share/xdg/}"

if [ -e "/etc/locale.conf" ]; then
    . /etc/locale.conf
fi

export LANG LANGUAGE LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT LC_IDENTIFICATION

# End /usr/share/defaults/etc/profile.d/10-xdg.sh
