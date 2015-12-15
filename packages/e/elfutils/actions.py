#!/usr/bin/python

from pisi.actionsapi import get, autotools, pisitools


def setup():
    libdir = "lib64" if get.buildTYPE() != "emul32" else "lib32"
    autotools.configure("--program-prefix=eu \
                         --libdir=/usr/%s \
                         --disable-static" % libdir)


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    if get.buildTYPE() == "emul32":
        pisitools.removeDir("/usr/lib32/elfutils")
