#!/usr/bin/python
import piksemel
import os
import os.path


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
            cmd = "dracut -N -f --kver %s" % version
            os.system(cmd)
            if os.path.exists("/proc/cmdline"):
                os.system("/usr/sbin/update-grub")
            break


def setupPackage(metapath, filepath):
    updateInitrd(filepath)


def postCleanupPackage(metapath, filepath):
    # TODO: Remove old initramfs!
    pass
