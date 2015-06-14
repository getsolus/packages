#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

# Prevent S/V with girscanner
shelltools.export("HOME", get.workDIR())

def setup():
    autotools.configure("--disable-static")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Ensure docs are installed in main library package
    pisitools.dodoc("COPYING", "COPYING.GPL", "ChangeLog", "AUTHORS")
