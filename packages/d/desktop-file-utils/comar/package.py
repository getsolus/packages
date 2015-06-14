#!/usr/bin/env python
import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    # Generate the known desktop database from /usr/share/applications
    os.system ("/usr/bin/update-desktop-database")
