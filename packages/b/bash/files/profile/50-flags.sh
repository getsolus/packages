# Begin /usr/share/defaults/etc/profile.d/50-flags.sh

if [ -z "${CFLAGS}" ]; then
    export CFLAGS="-g -O3 -feliminate-unused-debug-types -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=32 -Wformat -Wformat-security -fasynchronous-unwind-tables -ftree-loop-distribute-patterns -fno-semantic-interposition -ftree-vectorize -ftree-loop-vectorize -Wp,-D_REENTRANT"
fi

if [ -z "${CXXFLAGS}" ]; then
    export CXXFLAGS="-g -O3 -feliminate-unused-debug-types -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=32 -fasynchronous-unwind-tables -ftree-loop-distribute-patterns -fno-semantic-interposition -ftree-vectorize -ftree-loop-vectorize -Wp,-D_REENTRANT"
fi

if [ -z "${LDFLAGS}" ]; then
    export LDFLAGS="-Wl,-z -Wl,now -Wl,-z -Wl,relro"
fi

if [ -z "${FCFLAGS}" ]; then
    export FCFLAGS="-g -O3 -feliminate-unused-debug-types -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=32 -fasynchronous-unwind-tables -ftree-loop-distribute-patterns -fno-semantic-interposition -ftree-vectorize -ftree-loop-vectorize -Wp,-D_REENTRANT"
fi

if [ -z "${FFLAGS}" ]; then
    export FFLAGS="-g -O3 -feliminate-unused-debug-types -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=32 -fasynchronous-unwind-tables -ftree-loop-distribute-patterns -fno-semantic-interposition -ftree-vectorize -ftree-loop-vectorize -Wp,-D_REENTRANT"
fi

# End /usr/share/defaults/etc/profile.d/50-flags.sh
