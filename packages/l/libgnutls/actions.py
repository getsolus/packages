#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
import shutil

def setup():
    libdir = "/usr/lib64" if get.buildTYPE() != "emul32" else "/usr/lib32"


    confOpts = "--prefix=/usr \
                --libdir=%s \
                --mandir=/usr/share/man \
                --sysconfdir=/etc \
                --docdir=/usr/share/doc \
                --datarootdir=/usr/share \
                --with-default-trust-store-file=/etc/ssl/ca-certificates.crt \
                --disable-static" % libdir

    if get.buildTYPE() == "emul32":
        shelltools.export("CFLAGS", get.CFLAGS().replace("-march=x86-64", "-march=i686"))
        shelltools.export("CXXFLAGS", get.CXXFLAGS().replace("-march=x86-64", "-march=i686"))
        shelltools.system("linux32 ./configure %s" % confOpts)
    else:
        shelltools.system("./configure %s" % confOpts)

def build():
    autotools.make("-j1")

def install():
    idir = get.installDIR()
    # Force to subdirectory so we dont trash 64-bit installs
    if get.buildTYPE() == "emul32":
        idir += "/derpmcderp"

    autotools.rawInstall("DESTDIR=%s" % idir)

    if get.buildTYPE() == "emul32":
        pisitools.dodir("/usr")
        shelltools.system("mv \"%s/usr/lib32\" \"%s/usr/.\"" % (idir, get.installDIR()))
        shutil.rmtree(idir)
        return

    # Install docs
    autotools.make("-C doc/reference install-data-local DESTDIR=%s" % get.installDIR())
    pisitools.dodoc("COPYING", "COPYING.LESSER", "ChangeLog")
