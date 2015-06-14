#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.configure("--disable-static \
                         --libexecdir=/usr/lib/glib-networking \
                         --with-ca-certificates=/etc/ssl/certs/ca-certificates.crt")
def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc("COPYING")
