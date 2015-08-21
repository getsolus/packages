#!/usr/bin/python
import piksemel
import os
import os.path
import shutil

def updateSystemConfig(filepath):
    parse = piksemel.parse(filepath)

    shouldUser = False
    shouldTmp = False

    for xmlfile in parse.tags("File"):
        path = xmlfile.getTagData("Path")
        if not path.startswith("/"):
            path = "/%s" % path # Just in case
        if path.startswith("/usr/lib/tmpfiles.d") or path.startswith("/usr/lib64/tmpfiles.d"):
            shouldTmp = True
        if path.startswith("/usr/lib/sysusers.d") or path.startswith("/usr/lib64/sysusers.d"):
            shouldUser = True
        if shouldUser and shouldTmp:
            break

    if shouldUser:
        os.system("/usr/bin/systemd-tmpfiles --create")
    if shouldTmp:
        os.system("/usr/bin/systemd-sysusers")


def setupPackage(metapath, filepath):
    updateSystemConfig(filepath)


def postCleanupPackage(metapath, filepath):
    updateSystemConfig(filepath)
