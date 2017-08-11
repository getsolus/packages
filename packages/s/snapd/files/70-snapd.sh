# Begin /usr/share/defaults/etc/profile.d/70-snapd.sh

export PATH="$PATH:/snap/bin"

if [ -z "$XDG_DATA_DIRS" ]; then
    XDG_DATA_DIRS="/usr/share/:/usr/local/share/:/var/lib/snapd/desktop"
else
    XDG_DATA_DIRS="$XDG_DATA_DIRS:/var/lib/snapd/desktop/"
fi

# End /usr/share/defaults/etc/profile.d/70-snapd.sh
