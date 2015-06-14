#!/usr/bin/python


from pisi.actionsapi import autotools, pisitools


def setup():
    autotools.configure("--disable-static --enable-shared")


def build():
    autotools.make()


def install():
    autotools.install()

    pisitools.dodoc("ChangeLog", "COPYING", "AUTHORS")
