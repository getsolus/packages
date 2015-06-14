#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--with-gtk")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
