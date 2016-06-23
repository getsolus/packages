# Begin /usr/share/defaults/etc/profile.d/50-flags.sh

if [ -z "${CFLAGS}" ]; then
    export CFLAGS="-mtune=generic -march=x86-64 -ftree-vectorize -g2 -O2 -pipe -fPIC -Wformat -Wformat-security -fno-omit-frame-pointer -fstack-protector-strong --param ssp-buffer-size=4 -fexceptions -D_FORTIFY_SOURCE=2 -feliminate-unused-debug-types -Wno-error -Wp,-D_REENTRANT"
fi

if [ -z "${CXXFLAGS}" ]; then
    export CXXFLAGS="-mtune=generic -march=x86-64 -ftree-vectorize -g2 -O2 -pipe -fPIC -Wformat -Wformat-security -fno-omit-frame-pointer -fstack-protector-strong --param ssp-buffer-size=4 -fexceptions -D_FORTIFY_SOURCE=2 -feliminate-unused-debug-types -Wno-error -Wp,-D_REENTRANT"
fi

if [ -z "${LDFLAGS}" ]; then
    export LDFLAGS="-Wl,--copy-dt-needed-entries -Wl,-O1 -Wl,-z,relro -Wl,-z,now"
fi

if [ -z "${FCFLAGS}" ]; then
    export FCFLAGS="${CFLAGS}"
fi

if [ -z "${FFLAGS}" ]; then
    export FFLAGS="${CFLAGS}"
fi

# End /usr/share/defaults/etc/profile.d/50-flags.sh
