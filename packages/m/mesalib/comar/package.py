#!/usr/bin/env python
import os
import os.path

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    try:
        os.system("/usr/bin/linux-driver-management configure gpu")
    except Exception, e:
        print "Post-install error: %s" % e
