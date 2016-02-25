
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.export("CFLAGS", get.CFLAGS().replace("-Wl,-z,now", ""))
    shelltools.export("LDFLAGS", get.LDFLAGS().replace("-Wl,-z,now", ""))
    autotools.configure("--prefix=/usr\
                         --disable-static")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
