
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--disable-static \
                         --enable-ogg \
                         --enable-sse \
                         --disable-doxygen-docs \
                         --disable-dependency-tracking")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("COPYING.GPL", "AUTHORS")
