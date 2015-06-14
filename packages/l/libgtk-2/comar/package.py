#!/usr/bin/env python
import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
	# Update the known input method modules
	# Even if we push a package update, this is automatically updated
	# on the client system
	os.system ("gtk-query-immodules-2.0 > /etc/gtk-2.0/gtk.immodules")
	
