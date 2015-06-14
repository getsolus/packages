
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--disable-static")

def build():
    autotools.make()

def install():
    autotools.install()

    pisitools.dodoc("AUTHORS", "COPYING")

    pisitools.domove("/usr/share/doc/libogg-1.3.0", "/usr/share/doc/libogg-docs")
