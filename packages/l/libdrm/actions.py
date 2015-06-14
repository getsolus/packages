#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    # Disable linking to thread-stubs
    shelltools.system("sed -e \"/pthread-stubs/d\" -i configure.ac")

    autotools.autoreconf("-fi")
    autotools.configure("--disable-static --enable-udev --prefix=/usr")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc("README")
