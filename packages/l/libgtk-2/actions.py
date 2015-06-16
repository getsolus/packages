#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
shelltools.export ("HOME", get.workDIR())

def setup():
    os.system("sed -i 's#l \(gtk-.*\).sgml#& -o \1#' docs/faq/Makefile.in")
    os.system("sed -i 's#l \(gtk-.*\).sgml#& -o \1#' docs/tutorial/Makefile.in")
    autotools.configure("--disable-static \
                         --enable-xinerama \
                         --with-x \
                         --enable-explicit-deps")

def build():
    autotools.make()

def install():
    autotools.rawInstall("RUN_QUERY_IMMODULES_TEST=false DESTDIR=%s" % get.installDIR())
    pisitools.rename("/usr/bin/gtk-update-icon-cache", "gtk-update-icon-cache-2.0")
