
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
import shutil

shelltools.export("HOME", get.workDIR())

def setup():
    if get.buildTYPE() == "emul32":
        libdir = "/usr/lib32"
        exOpts = "--libdir=/usr/lib32 --disable-defaults-service"
    else:
        libdir = "/usr/lib64"
        exOpts = "--libdir=/usr/lib64"

    autotools.configure("--sysconfdir=/etc \
                         --libexecdir=%s/GConf \
                         --disable-orbit \
                         --disable-static %s" % (libdir, exOpts))

def build():
    autotools.make()

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
    
    pisitools.dosym("/etc/gconf/gconf.xml.defaults", "/etc/gconf/gconf.xml.system")

    pisitools.dodoc("ChangeLog", "COPYING")
