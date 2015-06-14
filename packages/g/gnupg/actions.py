#!/usr/bin/python


from pisi.actionsapi import autotools, get, pisitools


def setup():
    autotools.configure("--libexecdir=/usr/lib/GnuPG")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dosym("/usr/bin/gpg2", "/usr/bin/gpg")
    pisitools.dodoc("AUTHORS", "COPYING")
