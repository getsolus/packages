#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.rawConfigure("--bindir=/bin\
                             --mandir=/usr/share/man")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Make dash the default shell on our system
    pisitools.dosym("/bin/dash", "/usr/bin/dash")
