#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.configure("--libdir=/usr/lib64 \
                         --disable-idn \
                         --disable-meanwhile \
                         --disable-schemas-install \
                         --disable-tcl")

def build():
    autotools.make()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
    pisitools.removeDir("/usr/lib")
