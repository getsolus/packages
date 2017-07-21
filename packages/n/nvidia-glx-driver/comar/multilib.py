#!/usr/bin/env python
import os
import os.path

kver = "4.9.39-35.lts"

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    try:
        os.system("/usr/bin/linux-driver-management configure gpu")
    except Exception, e:
        print "Post-install error: %s" % e

def postRemove():
    try:
        os.system("/usr/bin/linux-driver-management configure gpu")
    except Exception, e:
        print "Post-remove error: %s" % e
