# Begin /usr/share/defaults/etc/profile.d/50-flags.sh

if [ -z "${CFLAGS}" ]; then
    export CFLAGS="-g2 -O3 -pipe -fPIC -Wformat -Wformat-security -fno-omit-frame-pointer -fexceptions -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param ssp-buffer-size=32 -fasynchronous-unwind-tables -ftree-vectorize -feliminate-unused-debug-types -Wall -Wno-error -Wp,-D_REENTRANT"
fi

if [ -z "${CXXFLAGS}" ]; then
    export CXXFLAGS="-g2 -O3 -pipe -fPIC -fno-omit-frame-pointer -fexceptions -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param ssp-buffer-size=32 -fasynchronous-unwind-tables -ftree-vectorize -feliminate-unused-debug-types -Wall -Wno-error -Wp,-D_REENTRANT"
fi

if [ -z "${LDFLAGS}" ]; then
    export LDFLAGS="-Wl,-z,relro -Wl,-z,now"
fi

if [ -z "${FCFLAGS}" ]; then
    export FCFLAGS="-g2 -O3 -pipe -fPIC -fno-omit-frame-pointer -fexceptions -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param ssp-buffer-size=32 -fasynchronous-unwind-tables -ftree-vectorize -feliminate-unused-debug-types -Wall -Wno-error -Wp,-D_REENTRANT"
fi

if [ -z "${FFLAGS}" ]; then
    export FFLAGS="-g2 -O3 -pipe -fPIC -fno-omit-frame-pointer -fexceptions -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param ssp-buffer-size=32 -fasynchronous-unwind-tables -ftree-vectorize -feliminate-unused-debug-types -Wall -Wno-error -Wp,-D_REENTRANT"
fi

# End /usr/share/defaults/etc/profile.d/50-flags.sh
