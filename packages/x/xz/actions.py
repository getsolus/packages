
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    cflags = get.CFLAGS()
    cflags += " -D_FILE_OFFSET_BITS=64"
    shelltools.export("CFLAGS", cflags)
    autotools.configure("--prefix=/usr --disable-static")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dosym("/usr/lib/liblzma.so", "/lib/liblzma.so")
