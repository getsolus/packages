
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import shutil
import os

# Required for girscanner
shelltools.export ("HOME", get.installDIR())

def setup():
    # TODO: Add Jasper support
    libdir="/usr/lib64"
    prefix = "/usr"
    if get.buildTYPE() == "emul32":
        libdir = "/usr/lib32"
        prefix = "/emul32"

    autotools.configure("--disable-static\
                         --prefix=%s \
                         --libdir=%s \
                         --with-x11" % (prefix, libdir))

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    bdir = os.path.join(get.installDIR(), ".cache")
    # 32-bit only, 64-bit unaffected
    if os.path.exists(bdir):
        shutil.rmtree("%s/.cache" % get.installDIR())
