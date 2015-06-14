#!/usr/bin/python


from pisi.actionsapi import autotools, shelltools, get, pisitools

def setup():
    pisitools.dosed("configure.in", "AM_CONFIG_HEADER", "AC_CONFIG_HEADERS")
    autotools.autoreconf()
    autotools.configure()

def build():
    autotools.automake()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
