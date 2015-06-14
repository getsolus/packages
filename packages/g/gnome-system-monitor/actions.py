#!/usr/bin/python

from pisi.actionsapi import get, autotools, pisitools


def setup():
    autotools.configure()


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # No KDE in Evolve OS
    pisitools.remove("/usr/share/applications/gnome-system-monitor-kde.desktop")
    pisitools.dodoc("COPYING", "ChangeLog", "AUTHORS")
