#!/usr/bin/python
import piksemel
import os
import os.path
import shutil

def cleanupOldImages():
    """ Legacy paths """
    images = glob.glob("/boot/initramfs-*.img")
    for image in images:
        try:
            os.remove(image)
        except Exception, e:
            continue

def updateCBM(filepath):
    parse = piksemel.parse(filepath)
    updates = False

    for xmlfile in parse.tags("File"):
        path = xmlfile.getTagData("Path")
        if not path.startswith("/"):
            path = "/%s" % path # Just in case
        # Kernel update
        if path.startswith("/lib/modules"):
            updates = True
            break
        # Goofiboot update
        if path.startswith("/usr/lib/goofiboot") or path.startswith("/usr/lib64/goofiboot"):
            updates = True
            break

    if not updates:
        return

    cleanupOldImages()
    try:
        os.system("clr-boot-manager update")
    except Exception, e:
        print("Failed to run clr-boot-manager: %s" % e)

def setupPackage(metapath, filepath):
    updateCBM(filepath)

def postCleanupPackage(metapath, filepath):
    # TODO: Remove old initramfs!
    pass
