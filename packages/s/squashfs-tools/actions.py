#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools


def build():
    autotools.make("-C squashfs-tools XZ_SUPPORT=1 LZ4_SUPPORT=1")


def install():
    pisitools.dobin("squashfs-tools/mksquashfs")
    pisitools.dobin("squashfs-tools/unsquashfs")

    pisitools.dodoc("COPYING")
