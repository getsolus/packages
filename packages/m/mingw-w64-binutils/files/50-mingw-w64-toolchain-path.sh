# Begin /usr/share/defaults/etc/profile.d/50-mingw-w64-toolchain-path.sh

export MINGW_TOOLCHAIN_ROOT="/usr/share/mingw-w64"
export PATH="$PATH:$MINGW_TOOLCHAIN_ROOT/bin"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MINGW_TOOLCHAIN_ROOT/i686-w64-mingw32/lib"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$MINGW_TOOLCHAIN_ROOT/x86_64-w64-mingw32/lib"

# End /usr/share/defaults/etc/profile.d/50-mingw-w64-toolchain-path.sh
