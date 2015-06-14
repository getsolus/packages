
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.export ("HOME", get.workDIR())
    autotools.configure ("--prefix=/usr\
                          --sysconfdir=/etc \
                          --localstatedir=/var \
                          --libexecdir=/usr/lib/polkit-1 \
                          --with-os-type=SolusOS \
                          --enable-libsystemd-login=yes \
                          --enable-introspection=yes \
                          --disable-gtk-doc \
                          --disable-gtk-doc-html \
                          --disable-man-pages \
                          --disable-static")

def build():
    shelltools.export ("HOME", get.workDIR())
    autotools.make ()

def install():
    shelltools.export ("HOME", get.workDIR())

    # Must use rawInstall, or systemd files aren't installed
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc ("AUTHORS", "COPYING", "README")

    # Ensure our home directory always exists
    pisitools.dodir ("/var/empty")
