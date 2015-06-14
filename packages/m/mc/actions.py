#!/usr/bin/python

from pisi.actionsapi import autotools, get

def setup():
    autotools.configure("--with-screen=ncurses \
                         --enable-charset")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
