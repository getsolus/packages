#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools


def setup():
    autotools.configure("--enable-shared \
                         --with-x \
                         --enable-alsa \
                         --enable-pulseaudio \
                         --enable-pulseaudio-shared \
                         --enable-sse2 \
                         --enable-ssemath")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    
