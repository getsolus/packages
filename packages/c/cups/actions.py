
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.aclocal("-I config-scripts")
    autotools.configure("--libdir=/usr/lib \
                         --without-rcdir \
                         --with-docdir=/usr/share/cups/doc \
                         --with-system-groups=lpadmin \
                         --enable-openssl \
                         --enable-systemd \
                         --enable-acl \
                         --enable-dbus \
                         --enable-libpaper ")

def build():
    autotools.make()

def install():
    autotools.rawInstall("BUILDROOT=%s" % get.installDIR() )

    pisitools.dodir("/usr/lib/systemd/system/printer.target.wants")
    pisitools.dodir("/usr/lib/systemd/system/sockets.target.wants")
    pisitools.dodir("/usr/lib/systemd/system/multi-user.target.wants")

    pisitools.dosym("/usr/lib/systemd/system/org.cups.cupsd.service", "/usr/lib/systemd/system/printer.target.wants/org.cups.cupsd.service")
    pisitools.dosym("/usr/lib/systemd/system/org.cups.cupsd.socket", "/usr/lib/systemd/system/sockets.target.wants/org.cups.cupsd.socket")
    pisitools.dosym("/usr/lib/systemd/system/org.cups.cupsd.path", "/usr/lib/systemd/system/multi-user.target.wants/org.cups.cupsd.path")
