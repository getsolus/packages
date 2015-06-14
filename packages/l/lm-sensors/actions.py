#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools

opts = "PREFIX=/usr MANDIR=/usr/share/man BUILD_STATIC_LIB=0"

def build():
    autotools.make(opts)


def install():
    autotools.rawInstall("%s DESTDIR=%s" % (opts, get.installDIR()))

    
