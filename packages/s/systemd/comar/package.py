#!/usr/bin/env python
import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    try:
        os.system("/usr/bin/systemd-sysusers")
        os.system("/usr/bin/systemd-tmpfiles --create")
        os.system("/usr/bin/udevadm hwdb --update")
    except Exception, e:
        pass
