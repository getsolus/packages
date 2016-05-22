#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
shelltools.export ("HOME", get.workDIR())

def setup():
    os.system("sed -i 's#l \(gtk-.*\).sgml#& -o \1#' docs/faq/Makefile.in")
    os.system("sed -i 's#l \(gtk-.*\).sgml#& -o \1#' docs/tutorial/Makefile.in")
    autotools.autoreconf()
    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib64"

    # Temporary, until we get emul32 cups
    confopts = "--disable-cups" if get.buildTYPE() == "emul32" else ""
    autotools.configure("--disable-static \
                         --libdir=%s \
                         --enable-xinerama \
                         --with-x \
                         --enable-explicit-deps %s" % (libdir, confopts))

def build():
    autotools.make()

def install():
    autotools.rawInstall("RUN_QUERY_IMMODULES_TEST=false DESTDIR=%s" % get.installDIR())
    if get.buildTYPE() != "emul32":
        pisitools.rename("/usr/bin/gtk-update-icon-cache", "gtk-update-icon-cache-2.0")
