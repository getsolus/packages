#!/usr/bin/python

from pisi.actionsapi import get, autotools, pisitools


def setup():
    autotools.configure("--libexecdir=/usr/lib/sudo \
                        --docdir=/usr/share/doc/sudo \
                        --with-all-insults \
                        --with-env-editor ")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("ChangeLog")
