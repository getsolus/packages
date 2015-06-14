#!/usr/bin/python

from pisi.actionsapi import get, autotools


def setup():
    autotools.configure("--program-prefix=eu \
                         --disable-static")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
