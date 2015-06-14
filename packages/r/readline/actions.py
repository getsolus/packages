#!/usr/bin/python
# -*- coding: utf-8 -*-
#

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

def setup():
    autotools.configure("--with-curses \
                         --disable-static \
                         --libdir=/usr/lib64")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s install" % get.installDIR())

    pisitools.removeDir("/usr/bin")
    pisitools.dosym("../usr/lib/libreadline.so.6.2", "/lib64/libreadline.so.2")
    pisitools.dohtml("doc/")
    pisitools.dodoc("CHANGELOG", "CHANGES", "README", "USAGE", "NEWS")
