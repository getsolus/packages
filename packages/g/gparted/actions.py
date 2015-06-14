#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools


def setup():
    autotools.autoreconf("-vfi")
    autotools.configure("--disable-scrollkeeper \
                         --disable-doc")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING")
