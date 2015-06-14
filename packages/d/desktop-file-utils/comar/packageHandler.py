#!/usr/bin/python

import piksemel
import os

def updateDesktopDatabase (filepath):
	parse = piksemel.parse (filepath)
	for xmlfile in parse.tags("File"):
		path = xmlfile.getTagData ("Path")
		if "/share/applications/" in path:
			os.system ("/usr/bin/update-desktop-database")
			break

def setupPackage (metapath, filepath):
    updateDesktopDatabase (filepath)

def postCleanupPackage (metapath, filepath):
    updateDesktopDatabase (filepath)
