#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--prefix=/usr\
                         --sysconfdir=/etc\
                         --enable-utf8")

def build():
    autotools.make()


def install():
    autotools.install()
    # Ship the sample nanorc with the package
    pisitools.insinto("/etc/", "doc/nanorc.sample", "nanorc")
