#!/usr/bin/python

# Based on original package in Pardus

from pisi.actionsapi import cmaketools
from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

WorkDir = "comar-3.0.3/comar"

def setup():
    cmaketools.configure("-DPYTHON_INCLUDE_DIR=/usr/include/python2.7 \
                          -DPYTHON_LIBRARY=/usr/lib/libpython2.7.so")

def build():
    autotools.make("VERBOSE=1")

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodir("/var/db")
