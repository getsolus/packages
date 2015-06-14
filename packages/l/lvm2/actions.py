#!/usr/bin/python


from pisi.actionsapi import pisitools, autotools, get

def setup():
    autotools.configure ("--prefix=/usr       \
                                              --exec-prefix=      \
                                              --with-confdir=/etc \
                                              --enable-applib     \
                                              --enable-cmdlib     \
                                              --enable-pkgconfig  \
                                              --enable-dmeventd   \
                                              --disable-udev_sync")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
