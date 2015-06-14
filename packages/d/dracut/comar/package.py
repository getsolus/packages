#!/usr/bin/env python
import os
import os.path

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    # Generate an initramfs for all installed kernels
    for possible in os.listdir ("/boot"):
        if possible.startswith ("kernel-") or possible.startswith ("vmlinuz-"):
            version = possible.split ("-")[1]
            cmd = "/sbin/depmod %s" % version
            os.system(cmd)
            cmd = "dracut -N -f --kver %s" % version
            os.system (cmd)

    # Determine whether to actually update grub or not.
    if os.path.exists("/proc/cmdline"):
        os.system ("/usr/sbin/update-grub")
