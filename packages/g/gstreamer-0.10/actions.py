#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

shelltools.export("HOME", get.workDIR())


def setup():
    autotools.configure("--with-package-name=\"GStreamer 0.10.36 SolusOS\" \
                         --with-package-origin=http://www.solusos.com \
                         --disable-static \
                         --libexecdir=/usr/lib \
                         --disable-check \
                         --enable-introspection=yes \
                         --disable-tests \
                         --disable-examples")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING")
