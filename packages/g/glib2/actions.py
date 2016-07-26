#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    libdir = "lib64" if get.buildTYPE() != "emul32" else "lib32"
    host = "" if get.buildTYPE() != "emul32" else "--build=i686-pc-linux-gnu --host=i686-pc-linux-gnu"
    autotools.configure("--with-pcre=system \
                         --libdir=/usr/%s %s" % (libdir, host))

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
