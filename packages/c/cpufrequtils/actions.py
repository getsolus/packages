#!/usr/bin/python


from pisi.actionsapi import autotools,get

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
