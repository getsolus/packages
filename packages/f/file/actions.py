#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools

IgnoreAutodep = True

def setup():
    autotools.configure("--disable-static \
                         --enable-shared")

def build():
    autotools.make()

def install():
    autotools.install()
