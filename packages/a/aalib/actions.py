#!/usr/bin/python

from pisi.actionsapi import pisitools, autotools,get

def setup():
    autotools.configure("--disable-static")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc("README","AUTHORS","ANNOUNCE", "COPYING", "ChangeLog")
