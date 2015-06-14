
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--enable-shared \
                     --disable-static")

def build():
    autotools.make ()

def install():
    autotools.install()
    pisitools.dodoc ("COPYING", "AUTHORS", "BUGS", "ChangeLog")
