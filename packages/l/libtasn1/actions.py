
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--disable-static")

def build():
    autotools.make ()

def install():
    autotools.install ()

    pisitools.dodoc ("NEWS", "ChangeLog")

    autotools.make ("-C doc/reference install-data-local DESTDIR=%s" % get.installDIR())
