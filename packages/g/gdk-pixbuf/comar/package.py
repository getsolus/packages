#!/usr/bin/env python
import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
	# Update the known gdk-pixbuf-query-loaders
	# Even if we push a package update, this is automatically updated
	# on the client system
	os.system ("gdk-pixbuf-query-loaders --update-cache")
	
