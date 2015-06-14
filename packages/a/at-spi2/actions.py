#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

# Required for girscanner
shelltools.export ("HOME", get.installDIR())

def setup():
    autotools.configure("--disable-static\
                         --prefix=/usr\
                         --sysconfdir=/etc\
                         --libexecdir=/usr/lib/at-spi2/core")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
