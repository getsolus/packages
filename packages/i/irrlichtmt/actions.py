#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools, shelltools

srcDir = "source/Irrlicht"


def build():
    shelltools.cd(srcDir)
    autotools.make("sharedlib NDEBUG=1")


def install():
    pisitools.insinto("/usr/include/irrlicht", "include/*")
    pisitools.dolib("lib/Linux/libIrrlicht.so.1.8.1")
    pisitools.dosym("/usr/lib/libIrrlicht.so.1.8.1", "/usr/lib/libIrrlicht.so")
    pisitools.dosym("/usr/lib/libIrrlicht.so.1.8.1", "/usr/lib/libIrrlicht.so.1.8")

    
