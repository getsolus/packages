
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.rawConfigure("--prefix=/usr \
                            --with-awk=/usr/bin/awk \
                            --with-gnu-ld \
                            --without-x")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dosym("eqn", "/usr/bin/geqn")
    pisitools.dosym("tbl", "/usr/bin/gtbl")
