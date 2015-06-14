#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

shelltools.export("HOME", get.workDIR())


def setup():
    autotools.configure("--disable-static \
                         --disable-mono       \
                         --disable-monodoc    \
                         --disable-python     \
                         --disable-qt3        \
                         --disable-qt4        \
                         --disable-gtk3        \
                         --disable-gtk         \
                         --enable-compat-libdns_sd \
                         --enable-core-docs   \
                         --with-distro=none")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("ChangeLog", "LICENSE")
    pisitools.removeDir("/var/run")
    pisitools.removeDir("/var")
    pisitools.removeDir("/usr/share/applications")
    pisitools.dosym("/usr/include/avahi-compat-libdns_sd/dns_sd.h", "/usr/include/dns_sd.h")
