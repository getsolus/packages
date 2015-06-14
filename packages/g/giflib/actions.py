#!/usr/bin/python

from pisi.actionsapi import pisitools, autotools,get

def setup():
    autotools.rawConfigure("--prefix=/usr \
                            --with-x \
                            --disable-static")



def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=\%s" % get.installDIR())

    pisitools.dohtml("doc/")
    pisitools.dodoc("README","AUTHORS","BUGS","NEWS")
