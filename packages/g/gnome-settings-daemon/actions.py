#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    # TODO: Investigate NM support
    autotools.configure("--disable-static \
                         --disable-man \
                         --libexecdir=/usr/lib/gnome-settings-daemon \
                         --enable-packagekit \
                         --disable-network-manager \
                         --enable-systemd")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING")
