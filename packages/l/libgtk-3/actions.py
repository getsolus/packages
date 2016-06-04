#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools
import shutil

shelltools.export ("HOME", get.workDIR())

def setup():
    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib64"
    autotools.autoreconf("-vfi")
    autotools.configure("--enable-gtk2-dependency \
                         --enable-wayland-backend \
                         --disable-packagekit     \
                         --prefix=/usr            \
                         --libdir=%s              \
                         --enable-x11-backend" % libdir)

def build():
    autotools.make()

def install():
    idir = get.installDIR()
    # Force to subdirectory so we dont trash 64-bit installs
    if get.buildTYPE() == "emul32":
        idir += "/derpmcderp"

    autotools.rawInstall ("DESTDIR=%s" % idir)

    if get.buildTYPE() == "emul32":
        pisitools.dodir("/usr")
        shelltools.system("mv \"%s/usr/lib32\" \"%s/usr/.\"" % (idir, get.installDIR()))
        shutil.rmtree(idir)
        return

    # Remove as its provided by GTK2 for now.
    # We may drop the --enable-gtk2-dependency and move tool to gtk-update-icon-cache-3.0
    pisitools.remove ("/usr/share/man/man1/gtk-update-icon-cache.1")
