# Begin /usr/share/defaults/etc/profile.d/50-umask.sh

if [ "`id -un`" = "`id -gn`" -a $EUID -gt 99 ]; then
  umask 002
else
  umask 022
fi

# End /usr/share/defaults/etc/profile.d/50-umask.sh
