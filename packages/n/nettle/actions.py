
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib64"

    autotools.configure("--libdir=%s --enable-shared" % libdir)
def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib64"

    for target in ["%s/libhogweed.so.4.2" % libdir, "%s/libnettle.so.6.2" % libdir]:
        shelltools.chmod("%s%s" % (get.installDIR(), target), mode=0755)

    pisitools.dodoc("nettle.html")
