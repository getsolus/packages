#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools


def build():
    autotools.make("linux")


def install():
    opts = "INSTALL_TOP=%s/usr TO_LIB=\"liblua.so liblua.so.5.1 liblua.so.5.1.5\" \
INSTALL_DATA=\"cp -d\" INSTALL_MAN=%s/usr/share/man/man1" % (get.installDIR(),get.installDIR())
    autotools.rawInstall(opts)

    wants = [ "*.html", "*.png", "*.css", "*.gif" ]
    for w in wants:
        pisitools.insinto("/usr/share/doc/lua", "doc/%s" % w)
