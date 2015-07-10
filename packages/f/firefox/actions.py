#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    pisitools.dosed("mozconfig", "##JOBCOUNT##", get.makeJOBS())

def build():
    autotools.make("-f client.mk")


def install():
    autotools.rawInstall("-f client.mk install INSTALL_SDK= DESTDIR=%s" % get.installDIR())
    pisitools.dosym("/usr/lib/firefox-39.0/browser/icons/mozicon128.png",
                     "/usr/share/pixmaps/firefox.png")
    pisitools.dodir("/usr/lib/mozilla/plugins")
    pisitools.dosym("/usr/lib/mozilla/plugins",
                    "/usr/lib/firefox-39.0/plugins")

