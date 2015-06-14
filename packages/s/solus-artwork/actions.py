#!/usr/bin/python

from pisi.actionsapi import autotools, pisitools

def setup():
    autotools.configure()

def build():
    autotools.make()

def install():
    autotools.install()
    pisitools.dosym("/usr/share/themes/Vertex", "/usr/share/themes/Evotex")
    # Compatibility symlink..
    pisitools.dosym("/usr/share/backgrounds/solus", "/usr/share/backgrounds/evolve-os")
