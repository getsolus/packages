#!/usr/bin/python

import piksemel
import os

def updateSystemFonts (filepath):
	parse = piksemel.parse (filepath)
	for xmlfile in parse.tags("File"):
		path = xmlfile.getTagData ("Path")
		if "/share/fonts/" in path:
			os.system ("fc-cache -fv")
			break

def setupPackage (metapath, filepath):
    updateSystemFonts (filepath)

def postCleanupPackage (metapath, filepath):
    updateSystemFonts (filepath)
