#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--disable-static \
                         --enable-gtk2 \
                         --enable-gtk3 \
                         --enable-alsa \
                         --enable-pulse \
                         --with-builtin=dso \
                         --disable-oss")
def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
