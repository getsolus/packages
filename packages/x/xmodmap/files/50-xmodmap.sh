# Begin /usr/share/defaults/etc/profile.d/50-xmodmap.sh

if [ -s "$HOME/.Xmodmap" ]; then
    xmodmap "$HOME/.Xmodmap"
fi

# End /usr/share/defaults/etc/profile.d/50-xmodmap.sh
