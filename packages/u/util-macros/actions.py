#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--disable-static")

def build():
    pass

def install():
    autotools.install()
    pisitools.dodoc("README", "COPYING", "ChangeLog")
