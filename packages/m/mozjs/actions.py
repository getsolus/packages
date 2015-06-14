#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools, shelltools


def setup():
    shelltools.cd("js/src")
    # Because readline. Officially sick of working around ncurses and readline woes.
    shelltools.export("LIBS", "-lncursesw")
    autotools.configure("--enable-readline \
                         --enable-threadsafe \
                         --with-system-ffi \
                         --with-system-nspr")


def build():
    shelltools.cd("js/src")
    autotools.make()


def install():
    shelltools.cd("js/src")
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
