
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

shelltools.export("HOME", get.workDIR())


def setup():
    # Probably revisit and sync vt's with plymouth
    # after we get X starting faster
    autotools.configure("--disable-static \
                         --with-user=\"gdm\" \
                         --with-group=\"gdm\" \
                         --without-plymouth \
                         --with-systemd \
                         --with-default-pam-config=lfs \
                         --enable-introspection \
                         --enable-console-helper \
                         --enable-gdm-xsession \
                         --with-at-spi-registryd-directory=/usr/lib/at-spi2/core \
                         --with-check-accelerated-directory=/usr/lib/gnome-session  \
                         --without-console-kit \
                         --with-initial-vt=7 \
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
