#!/usr/bin/env python
import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
	# Update the known input method modules
	# Even if we push a package update, this is automatically updated
	# on the client system
	os.system ("gtk-query-immodules-3.0 --update-cache")
	
	# For every package that ships GSettings schemas, we must recompile
	# the system's schemas
	os.system ("glib-compile-schemas /usr/share/glib-2.0/schemas")
