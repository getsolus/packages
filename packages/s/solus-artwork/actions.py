#!/usr/bin/python

from pisi.actionsapi import autotools, pisitools, shelltools, get

def setup():
    shelltools.system("autoreconf -vfi")
    shelltools.system("./configure --prefix=/usr")

def build():
    autotools.make()

def install():
    shelltools.system("make install DESTDIR=%s" % get.installDIR())
    pisitools.dosym("/usr/share/themes/Vertex", "/usr/share/themes/Evotex")
    # Compatibility symlink..
    pisitools.dosym("/usr/share/backgrounds/solus", "/usr/share/backgrounds/evolve-os")
