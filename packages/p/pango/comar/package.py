#!/usr/bin/env python
import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
	# Update the known pango modules
	# Even if we push a package update, this is automatically updated
	# on the client system
	os.system ("pango-querymodules --update-cache")
	
