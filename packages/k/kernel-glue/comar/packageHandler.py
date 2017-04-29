#!/usr/bin/python
import piksemel
import os
import os.path
import shutil
import glob

def updateCBM(filepath):
    parse = piksemel.parse(filepath)
    updates = False
    kversion = None

    os.environ['PATH'] = "/sbin:/bin:/usr/sbin:/usr/bin"

    for xmlfile in parse.tags("File"):
        path = xmlfile.getTagData("Path")
        if not path.startswith("/"):
            path = "/%s" % path # Just in case

        # Kernel update
        if path.startswith("/lib/modules") or path.startswith("/lib64/modules"):
            # Skip crankiness
            try:
                kversion = path.split("/")[3]
            except:
                kversion = None
                pass

            updates = True
            break
        # Goofiboot update
        if path.startswith("/usr/lib/goofiboot") or path.startswith("/usr/lib64/goofiboot"):
            updates = True
            break

    if not updates:
        return

    # Depmod the appropriate kernel if we can
    if kversion is not None:
        try:
            os.system("/sbin/depmod %s" % kversion)
        except Exception, e:
            print("Failed to run clr-boot-manager: %s" % e)

    # Always attempt to update CBM state
    try:
        os.system("/usr/bin/clr-update-wrapper")
    except Exception, e:
        print("Failed to run clr-boot-manager: %s" % e)

def setupPackage(metapath, filepath):
    updateCBM(filepath)

def postCleanupPackage(metapath, filepath):
    # TODO: Remove old initramfs!
    pass
