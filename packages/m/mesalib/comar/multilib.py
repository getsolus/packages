#!/usr/bin/env python
import os
import os.path

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    try:
        os.system("/usr/bin/gl-driver-switch set-link default")
    except Exception, e:
        print "Post-install error: %s" % e
