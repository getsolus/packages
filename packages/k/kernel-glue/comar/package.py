#!/usr/bin/env python
import os
import os.path

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    chrooted = False
    testPaths = [
        "/proc/1",
        "/sys/kernel",
        "/dev/shm",
        "/run/systemd",
    ]

    for p in testPaths:
        if not os.path.exists(p):
            chrooted = True

    try:
        st = os.stat('/')
        if st.st_ino != 2:
            chrooted = True
    except:
        chrooted = True

    if not chrooted:
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

    if os.path.exists("/usr/sbin/usysconf"):
        try:
            os.system("/usr/sbin/usysconf run")
        except:
            pass
