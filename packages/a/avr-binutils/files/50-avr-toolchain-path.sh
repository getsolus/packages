# Begin /usr/share/defaults/etc/profile.d/50-avr-toolchain-path.sh

export AVR_TOOLCHAIN_ROOT="/usr/share/avr"
export PATH="$PATH:$AVR_TOOLCHAIN_ROOT/bin"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$AVR_TOOLCHAIN_ROOT/lib"

# End /usr/share/defaults/etc/profile.d/50-avr-toolchain-path.sh