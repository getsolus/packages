#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    # TODO: Check systemd integration
    autotools.configure("--with-xkb-output=/var/lib/xkb \
                         --enable-install-setuid \
                         --enable-suid-wrapper \
                         --with-xkb-path=/usr/share/X11/xkb \
                         --with-fontrootdir=/usr/share/fonts \
                         --enable-glamor \
                         --enable-xwayland \
                         --enable-kdrive \
                         --enable-kdrive-kbd \
                         --enable-kdrive-evdev \
                         --enable-kdrive-mouse \
                         --enable-xephyr \
                         --disable-static")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Integrate with gl-driver-switch
    pisitools.dodir("/usr/lib/glx-provider/default")
    pisitools.domove("/usr/lib/xorg/modules/extensions/libglx.so", "/usr/lib/glx-provider/default/")
    pisitools.dosym("/usr/lib/glx-provider/default/libglx.so", "/usr/lib/glx-provider/default/libglx.so.1")
    pisitools.removeDir("/var/log")
