
#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    pisitools.dosed("configure.ac", "pthread-stubs", "")
    autotools.autoreconf("-fi")
    autotools.configure("--enable-xinput\
                         --docdir=/usr/share/doc/libxcb-1.11")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
