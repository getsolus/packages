#!/usr/bin/python

# Modified for SolusOS
# Based on original Pardus glibc packaging, needs audit

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

import os

IgnoreAutodep = True

WorkDir = "glibc-2.18"

defaultflags = "-O3 -g -U_FORTIFY_SOURCE -fno-strict-aliasing \
                -fomit-frame-pointer -mno-tls-direct-seg-refs"


sysflags = "-mtune=generic -march=x86-64" if get.ARCH() == "x86_64" \
           else "-mtune=atom -march=i686"

pkgworkdir = "%s/%s" % (get.workDIR(), WorkDir)

config = {
    "system":
    {
        "multi": False,
        "extraconfig": "--build=%s " % (get.HOST()),
        "coreflags": "",
        "libdir": "lib",
        "buildflags": "%s %s" % (sysflags, defaultflags),
        "builddir": "%s/build" % pkgworkdir
    }
}

ldconf32bit = """/lib32
/usr/lib32
"""
#/usr/local/lib32


def set_variables(cfg):
    shelltools.export("LANGUAGE", "C")
    shelltools.export("LANG", "C")
    shelltools.export("LC_ALL", "C")

    shelltools.export("CC", "gcc %s" % cfg["coreflags"])
    shelltools.export("CXX", "g++ %s" % cfg["coreflags"])

    shelltools.export("CFLAGS", cfg["buildflags"])
    shelltools.export("CXXFLAGS", cfg["buildflags"])


### functionize repetetive tasks ###
def libcSetup(cfg):
    set_variables(cfg)

    if not os.path.exists(cfg["builddir"]):
        shelltools.makedirs(cfg["builddir"])

    shelltools.cd(cfg["builddir"])
    shelltools.system("../configure \
                       --with-tls \
                       --with-__thread \
                       --enable-add-ons=nptl,libidn \
                       --enable-bind-now \
                       --enable-kernel=2.6.25 \
                       --enable-stackguard-randomization \
                       --without-cvs \
                       --without-gd \
                       --without-selinux \
                       --disable-profile \
                       --prefix=/usr \
                       --mandir=/usr/share/man \
                       --infodir=/usr/share/info \
                       --libexecdir=/usr/lib/misc \
                       --enable-obsolete-rpc \
                       %s " % cfg["extraconfig"])


def libcBuild(cfg):
    set_variables(cfg)

    shelltools.cd(cfg["builddir"])
    autotools.make()


def libcInstall(cfg):
    # not to bork locale/zone stuff
    set_variables(cfg)

    # install glibc/glibc-locale files
    shelltools.cd(cfg["builddir"])
    autotools.rawInstall("install_root=%s" % get.installDIR())

    # Some things want this, notably ash
    pisitools.dosym("libbsd-compat.a", "/usr/%s/libbsd.a" % cfg["libdir"])


### real actions start here ###
def setup():
    libcSetup(config["system"])


def build():
    libcBuild(config["system"])


def install():
    libcInstall(config["system"])

    # localedata can be shared between archs
    shelltools.cd(config["system"]["builddir"])
    autotools.rawInstall("install_root=%s localedata/install-locales"
                         % get.installDIR())

    # now we do generic stuff
    shelltools.cd(pkgworkdir)

    # We'll take care of the cache ourselves
    if shelltools.isFile("%s/etc/ld.so.cache" % get.installDIR()):
        pisitools.remove("/etc/ld.so.cache")

    # Prevent overwriting of the /etc/localtime symlink
    if shelltools.isFile("%s/etc/localtime" % get.installDIR()):
        pisitools.remove("/etc/localtime")

    # Nscd needs this to work
    pisitools.dodir("/var/run/nscd")
    pisitools.dodir("/var/db/nscd")

    if shelltools.isDirectory("%s/usr/share/zoneinfo" % get.installDIR()):
        pisitools.removeDir("/usr/share/zoneinfo")

    for i in ["zdump"]:
        if shelltools.isFile("%s/usr/sbin/%s" % (get.installDIR(), i)):
            pisitools.remove("/usr/sbin/%s" % i)

    pisitools.dodoc("BUGS", "ChangeLog*", "CONFORMANCE", "NAMESPACE", "NEWS",
                    "PROJECTS", "README*", "LICENSES")
