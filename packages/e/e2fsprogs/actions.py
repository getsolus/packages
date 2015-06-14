
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.configure("--prefix=/usr \
                         --with-root-prefix="" \
                         --enable-elf-shlibs \
                         --disable-libblkid \
                         --disable-libuuid \
                         --disable-uuidd")

def build():
    autotools.make("-j1")

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Remove fsck as its provided by util-linux
    pisitools.remove ("/sbin/fsck")
