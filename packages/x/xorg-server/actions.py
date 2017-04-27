#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools

def speed_opt(name, cflags):
    """ this package cannot yet be converted to ypkg, so emulates:
        https://github.com/solus-project/ypkg/blob/master/ypkg2/ypkgcontext.py#L53
    """
    fl = list(cflags.split(" "))
    opt = "-ffunction-sections -fasynchronous-unwind-tables -flto  -ftree-loop-distribute-patterns -ftree-vectorize -ftree-loop-vectorize -fno-semantic-interposition -O3 -falign-functions=32".split(" ")
    optimisations = ["-O%s" % x for x in range(0, 4)]
    optimisations.extend("-Os")

    fl = filter(lambda x: x not in optimisations, fl)
    fl.extend(opt)
    shelltools.export(name, " ".join(fl))
    return " ".join(fl)

def setup():
    cflags = speed_opt("CFLAGS", get.CFLAGS()).replace("-Wl,-z,now", "")
    cxxflags = speed_opt("CXXFLAGS", get.CXXFLAGS()).replace("-Wl,-z,now", "")
    shelltools.export("LDFLAGS", get.LDFLAGS().replace("-Wl,-z,now", ""))
    shelltools.export("AR", "gcc-ar")
    shelltools.export("RANLIB", "gcc-ranlib")
    shelltools.export("NM", "gcc-nm")
    shelltools.export("CFLAGS", cflags)
    shelltools.export("CXXFLAGS", cxxflags)

    autotools.autoreconf("-vfi")
    autotools.configure("--with-xkb-output=/var/lib/xkb \
                         --enable-install-setuid \
                         --enable-suid-wrapper \
                         --disable-systemd-logind \
                         --with-int10=x86emu \
                         --with-xkb-path=/usr/share/X11/xkb \
                         --with-fontrootdir=/usr/share/fonts \
                         --enable-glamor \
                         --enable-xwayland \
                         --enable-kdrive \
                         --enable-kdrive-kbd \
                         --enable-kdrive-evdev \
                         --enable-kdrive-mouse \
                         --enable-xephyr \
                         --enable-dri \
                         --enable-dri2 \
                         --enable-dri3 \
                         --enable-xcsecurity \
                         --enable-config-udev \
                         --enable-config-udev-kms \
                         --disable-selective-werror \
                         --disable-static")

def build():
    autotools.make("V=1")

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Integrate with gl-driver-switch
    pisitools.dodir("/usr/lib/glx-provider/default")
    pisitools.domove("/usr/lib/xorg/modules/extensions/libglx.so", "/usr/lib/glx-provider/default/")
    pisitools.dosym("/usr/lib/glx-provider/default/libglx.so", "/usr/lib/glx-provider/default/libglx.so.1")
    pisitools.removeDir("/var/log")
