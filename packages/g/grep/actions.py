
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.rawConfigure("--prefix=/usr \
                            --bindir=/bin")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dosym("/bin/grep", "/usr/bin/grep")
    pisitools.dosym("/bin/egrep", "/usr/bin/egrep")
    pisitools.dosym("/bin/fgrep", "/usr/bin/fgrep")
