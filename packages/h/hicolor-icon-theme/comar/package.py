#!/usr/bin/env python
import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
	# Rebuild all icon themes
    for possible in os.listdir ("/usr/share/icons"):
        os.system ("/usr/bin/gtk-update-icon-cache -ft \"/usr/share/icons/%s\"" % possible)
	
