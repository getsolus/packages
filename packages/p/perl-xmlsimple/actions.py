
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, perlmodules, pisitools


def setup():
    perlmodules.configure ()

def build():
    perlmodules.make ()

def install():
    perlmodules.install ()

    pisitools.dodoc ("LICENSE")
