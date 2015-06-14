
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--with-apr=/usr")

def build():
    autotools.make()

def install():
    autotools.install()
    pisitools.dodoc ("LICENSE", "NOTICE", "README")
