
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--disable-static \
                         --disable-sdltest \
                         --disable-examples")

def build():
    autotools.make()

def install():
    autotools.install()

    pisitools.dodoc("LICENSE", "AUTHORS", "COPYING")

    pisitools.domove("/usr/share/doc/libtheora-1.1.1", "/usr/share/doc/libtheora-docs")
