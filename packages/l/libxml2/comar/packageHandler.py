#!/usr/bin/python

import piksemel
import os

def updateXMLCatalog (filepath):
	parse = piksemel.parse (filepath)
	for xmlfile in parse.tags("File"):
		path = xmlfile.getTagData ("Path")
		if "/share/xml/" in path:
			os.system ("/usr/bin/build-docbook-catalog --version=4.5")
			break

def setupPackage (metapath, filepath):
    updateXMLCatalog (filepath)

def postCleanupPackage (metapath, filepath):
    updateXMLCatalog (filepath)
