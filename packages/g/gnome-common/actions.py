#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools
import os

def setup():
    autotools.configure()


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    for i in ["ax_check_enable_debug.m4", "ax_code_coverage.m4"]:
        os.unlink("%s/usr/share/aclocal/%s" % (get.installDIR(), i))
    pisitools.dodoc("ChangeLog", "COPYING")
