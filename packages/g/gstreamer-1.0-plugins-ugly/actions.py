#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools


def setup():
    autotools.configure("--disable-static \
                         --with-package-name=\"GStreamer Ugly Plugins 1.4.5 Solus\" \
                         --with-package-origin=\"https://solus-project.com\"")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("COPYING", "ChangeLog", "AUTHORS")
