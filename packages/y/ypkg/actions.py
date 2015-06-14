#!/usr/bin/python


from pisi.actionsapi import get, shelltools

def install():
    shelltools.system("DESTDIR=%s ./install.sh" % get.installDIR())
