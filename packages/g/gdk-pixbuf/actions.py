
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
    bindir = "/usr/bin"
    if get.buildTYPE() == "emul32":
        libdir = "/usr/lib32"
        prefix = "/emul32"
        bindir = "/usr/lib32/gdk-pixbuf-2.0/bin"

    autotools.configure("--disable-static\
                         --prefix=%s \
                         --libdir=%s \
                         --bindir=%s \
                         --with-x11" % (prefix, libdir, bindir))

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    bdir = os.path.join(get.installDIR(), ".cache")
    # 32-bit only, 64-bit unaffected
    if os.path.exists(bdir):
        shutil.rmtree("%s/.cache" % get.installDIR())
