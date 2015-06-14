
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--prefix=/usr \
                         --docdir=/usr/share/doc/pkg-config \
                         --with-internal-glib")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc ("AUTHORS", "COPYING", "ChangeLog", "README")
