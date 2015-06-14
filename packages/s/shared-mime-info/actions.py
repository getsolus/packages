
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.configure()

def build():
    autotools.make("-j1")

def install():
    autotools.install()

    pisitools.dodoc("README", "NEWS", "COPYING")
