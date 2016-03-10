#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    libdir = "lib64" if get.buildTYPE() != "emul32" else "lib32"
    autotools.configure("--with-pcre=system \
                         --libdir=/usr/%s" % libdir)

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
