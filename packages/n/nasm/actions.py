#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--prefix=/usr")

def build():
    autotools.make ()

def install():
    autotools.install ()

    # Install docs
    pisitools.dodoc ("doc/*.txt", "doc/*.ps", "doc/*.pdf", "doc/html/*.html")
    pisitools.doinfo ("doc/info/*")
