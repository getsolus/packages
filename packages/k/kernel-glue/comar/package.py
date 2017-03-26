#!/usr/bin/env python
import os
import shutil

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    if os.path.exists("/boot/efi/solus"):
        try:
            shutil.rmtree("/boot/efi/solus")
        except Exception, e:
            print("Failed to remove old Solus kernels: %s" % e)
    if os.path.exists("/boot/efi/loader/entries/solus.conf"):
        try:
            os.remove("/boot/efi/loader/entries/solus.conf")
        except Exception, e:
            print("Failed to remove old Solus UEFI config: %s" % e)
