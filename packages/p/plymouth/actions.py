#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools, libtools


def setup():
    autotools.configure("--enable-pango \
                         --enable-gtk \
                         --enable-drm \
                         --enable-systemd-integration \
                         --enable-gdm-transition \
                         --enable-pango \
                         --libdir=/usr/lib \
                         --without-system-root-install \
                         --with-logo=/usr/share/pixmaps/Solus.png")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING")
