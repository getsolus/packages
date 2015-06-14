
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--prefix=/usr")

def build():
    autotools.make ()

def install():
    autotools.install ()
