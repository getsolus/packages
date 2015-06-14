
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.aclocal("-I config-scripts")
    autotools.configure("--libdir=/usr/lib \
                         --without-rcdir \
                         --with-docdir=/usr/share/cups/doc \
                         --with-system-groups=lpadmin \
                         --enable-openssl \
                         --enable-acl \
                         --enable-dbus \
                         --enable-libpaper ")

def build():
    autotools.make()

def install():
    autotools.rawInstall("BUILDROOT=%s" % get.installDIR() )

    pisitools.removeDir("/usr/share/cups/banners")
    pisitools.removeDir("/usr/share/cups/data/testprint")

    shelltools.echo("%s/etc/cups/client.conf" % get.installDIR(), "ServerName /var/run/cups/cups.sock")
