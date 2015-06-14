#!/usr/bin/python


from pisi.actionsapi import autotools, shelltools, pisitools

def setup():
    shelltools.system("sed -i 's#) ytasm.*#)#' Makefile.in")
    autotools.configure()

def build():
    autotools.make()

def install():
    autotools.install()

    pisitools.dodoc("AUTHORS", "ChangeLog")
