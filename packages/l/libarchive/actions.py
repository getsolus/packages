#!/usr/bin/python


from pisi.actionsapi import autotools, get, pisitools
import os

def setup():
    autotools.configure("--prefix=/usr \
                         --disable-static")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("README", "NEWS", "COPYING")
