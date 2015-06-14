#!/usr/bin/python


# Inspired by Arch Linux's build for os-prober
# https://projects.archlinux.org/svntogit/community.git/tree/trunk/PKGBUILD?h=packages/os-prober

from pisi.actionsapi import shelltools, get, autotools, pisitools


def build():
    autotools.make ()

def install():
    pisitools.dobin("linux-boot-prober")
    pisitools.dobin("os-prober")
    pisitools.insinto("/usr/lib/os-prober", "newns", )
    pisitools.insinto("/usr/share/os-prober", "common.sh", )

    for d in ["os-probes",  "os-probes/mounted", "os-probes/init", "linux-boot-probes", "linux-boot-probes/mounted"]:
        pisitools.insinto("/usr/lib/%s" % d, "%s/common/*" % d)

        fpath = "%s/x86" % (d)
        print fpath
        if shelltools.can_access_directory(fpath):
            pisitools.insinto("/usr/lib/%s" % d, "%s/x86/*" % d)

    pisitools.insinto("/usr/lib/os-probes/mounted", "os-probes/mounted/powerpc/20macosx")

    pisitools.dodoc("debian/copyright")
    pisitools.dodir("/var/lib/os-prober/mounts")
