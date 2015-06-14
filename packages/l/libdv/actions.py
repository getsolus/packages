#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools


def setup():
    autotools.configure("--disable-static \
                         --disable-xv")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("COPYING", "ChangeLog", "AUTHORS")
