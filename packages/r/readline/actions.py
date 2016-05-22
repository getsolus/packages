#!/usr/bin/python
# -*- coding: utf-8 -*-
#

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get
from pisi.actionsapi import shelltools
import os
import shutil


def setup():
    libdir = "/usr/lib64" if get.buildTYPE() != "emul32" else "/usr/lib32"
    autotools.configure("--with-curses \
                         --prefix=/usr \
                         --disable-static \
                         --libdir=%s" % libdir)

def build():
    autotools.make("SHLIB_LIBS=-lncursesw")

def install():
    idir = get.installDIR()
    # Force to subdirectory so we dont trash 64-bit installs
    if get.buildTYPE() == "emul32":
        idir += "/derpmcderp"

    autotools.rawInstall ("DESTDIR=%s" % idir)
    libdir = "usr/lib64" if get.buildTYPE() != "emul32" else "usr/lib32"

    if get.buildTYPE() == "emul32":
        pisitools.dodir("/usr")
        shelltools.system("mv \"%s/usr/lib32\" \"%s/usr/.\"" % (idir, get.installDIR()))
        shutil.rmtree(idir)
        pisitools.dosym("../%s/libreadline.so.6.2" % libdir, "/lib32/libreadline.so.2")
        return

    pisitools.removeDir("/usr/bin")
    pisitools.dosym("../%s/libreadline.so.6.2" % libdir, "/lib64/libreadline.so.2")
    pisitools.dohtml("doc/")
    pisitools.dodoc("CHANGELOG", "CHANGES", "README", "USAGE", "NEWS")
