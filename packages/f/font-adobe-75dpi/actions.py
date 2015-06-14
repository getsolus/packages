#!/usr/bin/env python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--disable-static --prefix=/usr")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
