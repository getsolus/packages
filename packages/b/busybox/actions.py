#!/usr/bin/env python

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools

def build():
    autotools.make()
    autotools.make("busybox.links")

def install():
    pisitools.insinto("/bin", "busybox.links")
    pisitools.insinto("/bin", "busybox")
