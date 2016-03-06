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
        if "lib64/tmpfiles.d" in path or "lib/tmpfiles.d" in path:
            shouldTmp = True
        if "lib/sysusers.d" in path or "lib64/sysusers.d" in path:
            shouldUser = True
        if shouldUser and shouldTmp:
            break

    if shouldTmp:
        try:
            os.system("/usr/bin/systemd-tmpfiles --create")
        except Exception, e:
            pass
    if shouldUser:
        try:
            os.system("/usr/bin/systemd-sysusers")
        except Exception, e:
            pass

def setupPackage(metapath, filepath):
    updateSystemConfig(filepath)


def postCleanupPackage(metapath, filepath):
    updateSystemConfig(filepath)
