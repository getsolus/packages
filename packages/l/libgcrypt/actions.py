#!/usr/bin/python


from pisi.actionsapi import autotools, get, pisitools


def setup():
    autotools.configure("--with-gpg-error-prefix=/usr")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc("AUTHORS", "COPYING", "ChangeLog", "NEWS", "README",
                    "THANKS", "TODO", "VERSION")
