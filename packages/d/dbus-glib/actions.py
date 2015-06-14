
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--prefix=/usr \
                          --sysconfdir=/etc \
                          --localstatedir=/var \
                          --libexecdir=/usr/lib/dbus-1.0 \
                          --with-console-auth-dir=/run/console/\
                          --with-systemdsystemunitdir=/usr/lib/systemd/system\
                          --disable-static")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
