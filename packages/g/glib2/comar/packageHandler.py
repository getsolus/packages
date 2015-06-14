#!/usr/bin/python

import piksemel
import os

def updateGLibSchemas (filepath):
	parse = piksemel.parse (filepath)
	for xmlfile in parse.tags("File"):
		path = xmlfile.getTagData ("Path")
		if "/share/glib-2.0/schemas/" in path:
			os.system ("glib-compile-schemas /usr/share/glib-2.0/schemas")
			break

def setupPackage (metapath, filepath):
    updateGLibSchemas (filepath)

def postCleanupPackage (metapath, filepath):
    updateGLibSchemas (filepath)
