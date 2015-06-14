#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    # make distcheck, anyone?
    shelltools.system("sed -i s/-Werror// Makefile.in")
    autotools.configure("--disable-static")

def build():
    # Package fails parallel make
    autotools.make("-j1")

def install():
    autotools.install ()
    pisitools.dodoc ("COPYING", "AUTHORS", "ChangeLog", "README")
