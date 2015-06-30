#!/usr/bin/python


from pisi.actionsapi import shelltools, autotools, get, pisitools
import os
import shutil

FirmwareSource = "%s/linux-firmware-%s" % (get.workDIR(), get.srcVERSION())

Blacklisted = ["carl9170fw", "Makefile", "GPL-3"]

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    for potential in os.listdir (FirmwareSource):
        # Make sure to backup all licences
        if "LICENSE" in potential or "LICENCE" in potential:
            pisitools.dodoc (potential)
    for i in Blacklisted:
        p = os.path.join(get.installDIR(), "lib/firmware", i)
        if os.path.isfile(p):
            os.unlink(p)
        else:
            shutil.rmtree(p)
