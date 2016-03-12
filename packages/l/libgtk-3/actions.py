
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

shelltools.export ("HOME", get.workDIR())

def setup():
    autotools.autoreconf("-vfi")
    autotools.configure("--enable-gtk2-dependency \
                         --enable-wayland-backend \
                         --disable-packagekit     \
                         --enable-x11-backend")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Remove as its provided by GTK2 for now.
    # We may drop the --enable-gtk2-dependency and move tool to gtk-update-icon-cache-3.0
    pisitools.remove ("/usr/share/man/man1/gtk-update-icon-cache.1")
