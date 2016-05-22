
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.export ("HOME", get.workDIR())
    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib64"
    bindir = "/usr/lib32/pango/bin" if get.buildTYPE() == "emul32" else "/usr/bin"
    prefix = "/emul32" if get.buildTYPE() == "emul32" else "/usr"

    autotools.configure("--disable-static --enable-shared --prefix=%s --libdir=%s --bindir=%s" % (prefix, libdir, bindir))

def build():
    shelltools.export ("HOME", get.workDIR())
    autotools.make()

def install():
    shelltools.export ("HOME", get.workDIR())
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
