#!/usr/bin/python

from pisi.actionsapi import pisitools, autotools,get

def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s \
                          PREFIX=%s/usr \
                          INSTALL_MAN=%s/usr/share/man" % ((get.installDIR(),)*3))

    pisitools.dodoc("COPYING","README","*.txt")
