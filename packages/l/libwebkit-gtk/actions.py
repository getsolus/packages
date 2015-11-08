#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools, cmaketools

shelltools.export("HOME", get.workDIR())

def setup():
    cmaketools.configure("-DPORT=GTK -DCMAKE_SKIP_RPATH=ON")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
