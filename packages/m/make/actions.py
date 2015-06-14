#!/usr/bin/python

from pisi.actionsapi import pisitools, autotools,get

def setup():
    autotools.configure("--prefix=/usr\
                         --program-prefix=g ")

def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=\%s" % get.installDIR())

    pisitools.dosym("/usr/bin/gmake","/usr/bin/make")
    pisitools.dodoc("README","AUTHORS")
