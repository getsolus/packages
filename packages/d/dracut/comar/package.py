#!/usr/bin/env python
import os
import os.path
import shutil

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    # Generate an initramfs for all installed kernels
    for possible in os.listdir ("/boot"):
        if possible.startswith ("kernel-") or possible.startswith ("vmlinuz-"):
            version = possible.split ("-")[1]
            cmd = "/sbin/depmod %s" % version
            os.system(cmd)
            cmd = "dracut -N -f --kver %s" % version
            os.system (cmd)

            initname = "/boot/initramfs-%s.img" % version
            if os.path.exists("/boot/efi/solus"):
                try:
                    shutil.copy(initname, "/boot/efi/solus/initramfs")
                except Exception, e:
                    print("Failed to copy efi boot")

    # Determine whether to actually update grub or not.
    if os.path.exists("/proc/cmdline") and not os.path.exists("/sys/firmware/efi"):
        os.system ("/usr/sbin/update-grub")
