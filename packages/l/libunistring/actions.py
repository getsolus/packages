#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--disable-static")

def build():
    autotools.make()

def install():
    autotools.install()
    pisitools.dodoc ("ChangeLog", "BUGS", "AUTHORS", "COPYING.LIB",
                                     "COPYING", "README", "THANKS")
