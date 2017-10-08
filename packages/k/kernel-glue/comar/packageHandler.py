#!/usr/bin/python
import piksemel
import os
import os.path
import shutil
import glob

def updateSystemd(filepath):
    parse = piksemel.parse(filepath)

    shouldUser = False
    shouldTmp = False
    shouldHwdb = False
    shouldReload = False
    shouldRexec = False

    chrooted = False
    testPaths = [
        "/proc/1",
        "/sys/kernel",
        "/dev/shm",
        "/run/systemd",
    ]

    for p in testPaths:
        if not os.path.exists(p):
            chrooted = True

    try:
        st = os.stat('/')
        if st.st_ino != 2:
            chrooted = True
    except:
        chrooted = True

    for xmlfile in parse.tags("File"):
        path = xmlfile.getTagData("Path")
        if not path.startswith("/"):
            path = "/%s" % path # Just in case
        if "lib64/tmpfiles.d" in path or "lib/tmpfiles.d" in path:
            shouldTmp = True
        if "lib/sysusers.d" in path or "lib64/sysusers.d" in path:
            shouldUser = True
        if "lib/systemd/system" in path or "lib64/systemd/system" in path:
            shouldReload = True
        if path.startswith("/etc/udev/hwdb.d") or path.startswith("/usr/lib/udev/hwdb.d") or path.startswith("/usr/lib64/udev/hwdb.d"):
            shouldHwdb = True
        if shouldUser and shouldTmp and shouldHwdb:
            break

    if shouldUser:
        try:
            os.system("/usr/bin/systemd-sysusers")
        except Exception, e:
            pass

    if shouldTmp:
        try:
            os.system("/usr/bin/systemd-tmpfiles --create")
        except Exception, e:
            pass

    if shouldHwdb:
        try:
            os.system("/usr/bin/udevadm hwdb --update")
        except Exception, e:
            pass

    # These guys cannot be done in chroots, we'd break images completely
    if shouldReload and not chrooted:
        try:
            os.system("/usr/bin/systemctl daemon-reload")
        except Exception, e:
            pass

    if shouldRexec and not chrooted:
        try:
            os.system("/usr/bin/systemctl daemon-rexec")
        except Exception, e:
            pass

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
    updateSystemd(filepath)
    updateCBM(filepath)

def postCleanupPackage(metapath, filepath):
    # TODO: Remove old initramfs!
    pass
