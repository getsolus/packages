#!/usr/bin/python


from pisi.actionsapi import perlmodules, pisitools


def setup():
    perlmodules.configure()


def build():
    perlmodules.make()


def install():
    perlmodules.install()
    pisitools.remove("/usr/bin/instmodsh")
    pisitools.removeDir("/usr/bin")
    pisitools.remove("/usr/share/man/man1/instmodsh.1")
    
