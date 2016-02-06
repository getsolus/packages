#!/usr/bin/python


from pisi.actionsapi import pythonmodules, pisitools


def build():
    pythonmodules.compile()
    pythonmodules.compile(pyVer='3.5')


def install():
    pythonmodules.install()
    pythonmodules.install(pyVer='3.5')

    pisitools.dodoc("AUTHORS", "ChangeLog", "BUGS", "COPYING")
