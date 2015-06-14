#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.export("CONF_SHELL", "/bin/bash")
    autotools.configure("--disable-documentation")


def build():
    autotools.make()


def install():
    autotools.install()

    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING")
