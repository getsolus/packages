#!/usr/bin/python

from pisi.actionsapi import pisitools, autotools,get

def setup():
    autotools.configure("--prefix=/usr")



def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=\%s" % get.installDIR())

    pisitools.dodoc("README")

    # We maintain this symlink so pisi always uses the correct automake
    pisitools.dosym ("/usr/share/automake-1.14/", "/usr/share/gnuconfig")
