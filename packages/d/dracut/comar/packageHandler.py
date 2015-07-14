#!/usr/bin/python
import piksemel
import os
import os.path
import shutil

def updateInitrd(filepath):
    parse = piksemel.parse(filepath)
    for xmlfile in parse.tags("File"):
        path = xmlfile.getTagData("Path")
        if not path.startswith("/"):
            path = "/%s" % path # Just in case
        if path.startswith("/lib/modules"):
            # Handle the proper case of modules
            version = path.split("/")[3]
            cmd = "/sbin/depmod %s" % version
            os.system(cmd)
            cmd = "dracut  --lz4 -N -f --kver %s" % version
            os.system(cmd)

            initname = "/boot/initramfs-%s.img" % version
            if os.path.exists("/boot/efi/solus"):
                try:
                    shutil.copy(initname, "/boot/efi/solus/initramfs")
                except Exception, e:
                    print("Failed to copy efi boot")

            if os.path.exists("/proc/cmdline") and not os.path.exists("/sys/firmware/efi"):
                os.system("/usr/sbin/update-grub")
            break


def setupPackage(metapath, filepath):
    updateInitrd(filepath)


def postCleanupPackage(metapath, filepath):
    # TODO: Remove old initramfs!
    pass
