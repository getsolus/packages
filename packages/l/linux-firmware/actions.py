#!/usr/bin/python


from pisi.actionsapi import shelltools, get, pisitools
import os

FirmwareSource = "%s/linux-firmware-20140704" % get.workDIR()

Blacklisted = ["carl9170fw"]

Purged = ["GPL-3", "Makefile", "WHENCE"]

def install():
    for item in Purged:
        shelltools.unlink (item)
    for potential in os.listdir (FirmwareSource):
        # Make sure to backup all licences
        if "LICENSE" in potential or "LICENCE" in potential:
            pisitools.dodoc (potential)
        else:
            if not potential in Blacklisted:
                pisitools.insinto ("/lib/firmware", potential)
