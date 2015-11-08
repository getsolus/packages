#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools, cmaketools
import os

shelltools.export("HOME", get.workDIR())

def setup():
    del os.environ["LD_AS_NEEDED"]
    shelltools.export("CFLAGS", get.CFLAGS().replace("-Wl,-z,now", ""))
    shelltools.export("CXXFLAGS", get.CXXFLAGS().replace("-Wl,-z,now", ""))
    shelltools.export("LDFLAGS", get.LDFLAGS().replace("-Wl,-z,now", ""))
    cmaketools.configure("-DPORT=GTK -DCMAKE_SKIP_RPATH=ON")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
