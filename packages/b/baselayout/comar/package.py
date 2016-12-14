#!/usr/bin/env python
import os
import os.path
import shutil

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    interested = ["fstab", "group-", "gshadow-", "issue", "machine-id",\
                  "passwd-", "shadow", "group", "gshadow", "hosts",\
                  "passwd", "resolv.conf", "shadow-"]

    for item in interested:
        source_path = os.path.join ("/usr/share/baselayout", item)
        dest_path = os.path.join ("/etc", item)

        if not os.path.exists (dest_path):
            shutil.copy2 (source_path, dest_path)

    try:
        os.system("/sbin/ldconfig")
    except:
        pass
