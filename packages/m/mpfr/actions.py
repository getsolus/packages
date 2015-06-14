#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--enable-thread-safe\
                          --disable-static")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Make docs
    autotools.make("html")
    autotools.make("DESTDIR=%s install-html" % get.installDIR())
