
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    # Reconf to rebuild against a newer libtool
    autotools.autoreconf("--force --install --symlink")
    autotools.configure("--disable-zlib --datadir=/usr/share/hwids")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dosym("/usr/sbin/update-usbids.sh", "/usr/sbin/update-usbids")
    pisitools.dosym("/usr/sbin/update-usbids.sh", "/sbin/update-usbids")
