#!/usr/bin/python


from pisi.actionsapi import autotools, pisitools, get

def setup():
    autotools.configure("--disable-static \
                         --enable-libwebpmux \
                         --enable-libwebpdemux \
                         --enable-everything \
                         --enable-libwebpdecoder")

def build():
    autotools.make()


def install():
    autotools.install()

    pisitools.dodoc("COPYING")
