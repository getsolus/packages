
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib64"

    autotools.configure("--libdir=%s --enable-shared" % libdir)

# Program terminated.
# ActionsAPI [chmod]: No file matched pattern "/var/eopkg/nettle-2.7.1-8/install/usr/lib64/libhogweed.so.2.5".

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib64"

    for target in ["%s/libhogweed.so.2.5" % libdir, "%s/libnettle.so.4.7" % libdir]:
        shelltools.chmod("%s%s" % (get.installDIR(), target), mode=0755)

    pisitools.dodoc("nettle.html")
