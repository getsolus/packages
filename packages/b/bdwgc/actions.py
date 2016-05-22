#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
import shutil


def setup():
    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib64"
    shelltools.system("ln -s ../libatomic_ops/libatomic_ops-7.4.0 libatomic_ops")
    autotools.configure("--disable-static --libdir=%s" % libdir)

def build():
    autotools.make()

def install():
    idir = get.installDIR()
    # Force to subdirectory so we dont trash 64-bit installs
    if get.buildTYPE() == "emul32":
        idir += "/derpmcderp"

    autotools.rawInstall ("DESTDIR=%s" % idir)


    if get.buildTYPE() == "emul32":
        pisitools.dodir("/usr")
        shelltools.system("mv \"%s/usr/lib32\" \"%s/usr/.\"" % (idir, get.installDIR()))
        shutil.rmtree(idir)
        return
    
    pisitools.doman("%s/usr/share/gc/gc.man" % get.installDIR())
    shelltools.move("%s/usr/share/gc/" % get.installDIR(), "%s/usr/share/doc/bdwgc/" % get.installDIR())
    pisitools.rename("/usr/share/doc/bdwgc/README.linux", "README")
    pisitools.remove("/usr/share/doc/bdwgc/README.*")
    pisitools.dodoc ("ChangeLog")
