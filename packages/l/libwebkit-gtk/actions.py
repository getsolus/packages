#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools, cmaketools

shelltools.export("HOME", get.workDIR())

def setup():
    cmaketools.configure("-DPORT=GTK")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
