
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--disable-static")

def build():
    autotools.make()

def install():
    autotools.install()

    pisitools.dodoc("AUTHORS", "COPYING", "doc/Vorbis*")

    pisitools.domove("/usr/share/doc/libvorbis-1.3.3", "/usr/share/doc/libvorbis-docs")
