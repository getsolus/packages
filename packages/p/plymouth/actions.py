#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools, libtools


def setup():
    autotools.configure("--enable-pango \
                         --enable-gtk \
                         --enable-drm \
                         --enable-systemd-integration \
                         --enable-gdm-transition \
                         --enable-pango \
                         --with-logo=/usr/share/pixmaps/SolusOS_Splash.png")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING")
