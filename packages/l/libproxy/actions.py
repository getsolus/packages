#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools, cmaketools


def setup():
    cmaketools.configure()


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    
