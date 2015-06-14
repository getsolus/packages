#!/usr/bin/python


from pisi.actionsapi import autotools,get,pisitools

def setup():
    autotools.configure("--prefix=/usr \
                         --enable-nls \
                         --with-ssl=/usr \
                         --enable-ipv6")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc("AUTHORS", "CHANGES", "COPYING", "README")
