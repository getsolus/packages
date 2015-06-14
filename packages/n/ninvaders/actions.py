#!/usr/bin/python


from pisi.actionsapi import autotools, pisitools, get

def build():
    autotools.make()

def install():
    pisitools.dobin("nInvaders","/usr/bin")
    pisitools.dodoc("README","ChangeLog", "gpl.txt")
