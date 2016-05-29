#!/usr/bin/env python
import os
import os.path

kver = "4.4.11"

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    try:
        os.system("/usr/bin/gl-driver-switch set-link nvidia")
        os.system("/sbin/depmod %s" % kver)
        os.system("nvidia-xconfig")
    except Exception, e:
        print "Post-install error: %s" % e

def postRemove():
    try:
        os.system("/usr/bin/gl-driver-switch set-link default")
        if os.path.exists("/etc/X11/xorg.conf"):
            os.unlink("/etc/X11/xorg.conf")
    except Exception, e:
        print "Post-remove error: %s" % e
