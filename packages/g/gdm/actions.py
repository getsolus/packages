
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

shelltools.export("HOME", get.workDIR())


def setup():
    # Probably revisit and sync vt's with plymouth
    # after we get X starting faster
    autotools.configure("--disable-static \
                         --with-user=\"gdm\" \
                         --with-group=\"gdm\" \
                         --with-plymouth \
                         --with-default-pam-config=lfs \
                         --enable-introspection \
                         --enable-console-helper \
                         --enable-systemd-journal")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Enable ourselves by default(will conflict with lightdm)
    pisitools.dodir("/usr/lib/systemd/system/graphical.target.wants")
    pisitools.dosym("/usr/lib/systemd/system/gdm.service", "/usr/lib/systemd/system/displaymanager.service")
    pisitools.dosym("/usr/lib/systemd/system/gdm.service", "/usr/lib/systemd/system/graphical.target.wants/gdm.service")

    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING")
