#!/usr/bin/python


from pisi.actionsapi import autotools,get

def setup():
    autotools.configure("--prefix=/usr \
                         --without-rpmbuild \
                         --without-sendmail")

def build():
    autotools.make()

def install():
    autotools.rawInstall("BUILD_ROOT=%s" % get.installDIR())
