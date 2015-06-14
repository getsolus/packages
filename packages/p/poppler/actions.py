#!/usr/bin/python


from pisi.actionsapi import autotools, pisitools


def setup():
    autotools.configure("--disable-static \
                         --enable-xpdf-headers \
                         --enable-libtiff \
                         --enable-libjpeg \
                         --enable-libpng \
                         --enable-libcurl")


def build():
    autotools.make()


def install():
    autotools.install()

    pisitools.dodoc("COPYING", "ChangeLog", "AUTHORS")
