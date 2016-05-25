
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
import shutil


def setup():
    libdir = "/usr/lib64" if get.buildTYPE() != "emul32" else "/usr/lib32"
    autotools.configure ("--disable-static\
                          --disable-docs\
                          --libdir=%s\
                          --prefix=/usr \
                          --with-baseconfigdir=/usr/share/fonts \
                          --with-configdir=/usr/share/fonts/conf.d \
                          --docdir=/usr/share/doc/fontconfig-2.10.2" % libdir)

def build():
    autotools.make ()

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
