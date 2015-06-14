#!/usr/bin/python


from pisi.actionsapi import shelltools, get, waftools, pisitools


def setup():
    shelltools.export("PYTHON", "/usr/bin/python3")
    waftools.configure()


def build():
    waftools.make()


def install():
    waftools.install()

    pisitools.dodoc("COPYING.LESSER", "AUTHORS", "COPYING")
