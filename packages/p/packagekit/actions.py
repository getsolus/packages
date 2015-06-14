
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

shelltools.export ("HOME", get.workDIR())

def setup():
    autotools.configure ("--enable-pisi \
                          --with-default-backend=pisi \
                          --disable-dummy \
                          --disable-bash-completion \
                          --disable-man-pages \
                          --disable-static \
                          --libexecdir=/usr/lib/PackageKit \
                          --enable-systemd ")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR() )

    pisitools.dodoc ("AUTHORS", "ChangeLog", "COPYING")
