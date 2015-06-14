#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools


def setup():
    # Notes: Soon we'll switch to external fuse package, however this
    # package must be forced into system.base for now as a required
    # upgrade.  Later we'll move filesystems into a new component
    autotools.configure("--disable-static \
                         --disable-ldconfig")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Ensure ntfs-3g is default handler of ntfs mount ops
    pisitools.dosym("/bin/ntfs-3g", "/sbin/mount.ntfs")
    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING")
