#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    # We need to --enable-cogl in the future for cogl surface support
    # Disable xlib-xcb - its evil in cairo.
    autotools.configure("--disable-static \
                         --disable-xlib-xcb \
                         --enable-tee \
                         --enable-gl \
                         --enable-svg \
                         --disable-lto")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
