
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.configure ("--prefix=/usr       \
                          --bindir=/bin       \
                          --libdir=/lib       \
                          --sysconfdir=/etc   \
                          --disable-manpages  \
                          --with-xz           \
                          --with-zlib")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.domove ("/lib/pkgconfig", "/usr/lib/")
    # Provide links for module control
    for target in ["modprobe", "modinfo", "rmmod", "insmod", "depmod", "lsmod"]:
        pisitools.dosym ("/bin/kmod", "/sbin/%s" % target)
