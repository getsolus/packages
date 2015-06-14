#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools

# Circular deps  - woo
IgnoreAutodep = True

def setup():
    autotools.configure("--disable-login \
                         --disable-nologin \
                         --disable-chfn-chsh \
                         --disable-su \
                         --disable-static")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    # Conflicts with e2fsprogs
    pisitools.remove("/usr/share/man/man8/fsck.8")

    pisitools.dosym("/bin/mount", "/usr/bin/mount")
    pisitools.dosym("/bin/umount", "/usr/bin/umount")
