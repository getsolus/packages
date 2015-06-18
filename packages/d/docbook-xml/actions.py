#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools
from pisi.actionsapi.shelltools import system
import os

def install():
    docBookRoot = "/usr/share/xml/docbook/xml-dtd-4.5"
    pisitools.dodir ("/etc/xml")

    for copy in ["docbook.cat", "*.dtd", "ent/", "*.mod"]:
        copy_full = os.path.join (get.workDIR(), copy)
        pisitools.insinto (docBookRoot, copy_full)
