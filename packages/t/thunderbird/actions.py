#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    pisitools.dosed("mozconfig", "##JOBCOUNT##", get.makeJOBS())

def build():
    autotools.make("-f client.mk")


def install():
    autotools.rawInstall("-f client.mk install INSTALL_SDK= DESTDIR=%s" % get.installDIR())
    pisitools.dosym("/usr/lib/thunderbird-38.1.0/chrome/icons/mozicon128.png",
                     "/usr/share/pixmaps/thunderbird.png")
    pisitools.dosym("/usr/lib/mozilla/plugins",
                    "/usr/lib/thunderbird-38.1.0/plugins")
