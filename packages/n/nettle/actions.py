
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--libdir=/usr/lib")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    for target in ["/usr/lib/libhogweed.so.2.5", "/usr/lib/libnettle.so.4.7"]:
        shelltools.chmod("%s/%s" % (get.installDIR(), target), mode=0755)

    pisitools.dodoc("nettle.html")
