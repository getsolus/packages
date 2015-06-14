#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--disable-static \
                         --with-udev-rules-dir=/lib/udev/rules.d \
                         --without-hal-callouts-dir \
                         --without-hal-fdi-dir ")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("ChangeLog", "COPYING")
