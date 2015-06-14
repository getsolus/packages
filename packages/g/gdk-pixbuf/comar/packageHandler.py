#!/usr/bin/python

import piksemel
import os

def updatePixbufLoaders (filepath):
	parse = piksemel.parse (filepath)
	for xmlfile in parse.tags("File"):
		path = xmlfile.getTagData ("Path")
		if "/lib/gtk-2.0" in path or "/lib/gdk-pixbuf-2.0" in path:
			os.system ("gdk-pixbuf-query-loaders --update-cache")
			break

def setupPackage (metapath, filepath):
    updatePixbufLoaders (filepath)

def postCleanupPackage (metapath, filepath):
    updatePixbufLoaders(filepath)
