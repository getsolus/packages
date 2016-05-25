#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
shelltools.export ("HOME", get.workDIR())
import shutil

def setup():
    os.system("sed -i 's#l \(gtk-.*\).sgml#& -o \1#' docs/faq/Makefile.in")
    os.system("sed -i 's#l \(gtk-.*\).sgml#& -o \1#' docs/tutorial/Makefile.in")
    autotools.autoreconf()
    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib64"

    autotools.configure("--disable-static \
                         --libdir=%s \
                         --enable-xinerama \
                         --with-x \
                         --prefix=/usr \
                         --enable-explicit-deps \
                         --enable-cups" % libdir)

def build():
    autotools.make()

def install():
    idir = get.installDIR()
    if get.buildTYPE() == "emul32":
        idir += "/derpmcderp"

    autotools.rawInstall("RUN_QUERY_IMMODULES_TEST=false DESTDIR=%s" % idir)

    if get.buildTYPE() == "emul32":
        pisitools.dodir("/usr")
        shelltools.system("mv \"%s/usr/lib32\" \"%s/usr/.\"" % (idir, get.installDIR()))
        shutil.rmtree(idir)
        return

    pisitools.rename("/usr/bin/gtk-update-icon-cache", "gtk-update-icon-cache-2.0")
