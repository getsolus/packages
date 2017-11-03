#!/usr/bin/env python
import os
import os.path

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    if not os.path.exists("/usr/sbin/qol-assist"):
        try:
            if not os.path.exists("/var/lib/qol-assist"):
                os.mkdir("/var/lib/qol-assist")
            os.system("touch /var/lib/qol-assist/trigger")
        except:
                pass
    else:
        try:
            os.system("/usr/sbin/qol-assist trigger")
        except Exception, e:
            pass
