#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools


def setup():
    autotools.rawConfigure("--prefix=/usr \
                            --disable-static \
                            --enable-shared")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
