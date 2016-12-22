#!/usr/bin/python

import piksemel
import os

def updateDesktopDatabase(filepath):
    needUpdate = False
    parse = piksemel.parse(filepath)
    for xmlfile in parse.tags("File"):
        path = xmlfile.getTagData("Path")
        if "/share/applications/" in path:
            needUpdate = True
            break

    if needUpdate:
        os.system("/usr/bin/update-desktop-database")

def setupPackage(metapath, filepath):
    updateDesktopDatabase(filepath)

def postCleanupPackage(metapath, filepath):
    updateDesktopDatabase(filepath)
