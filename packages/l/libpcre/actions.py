
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.rawConfigure("--prefix=/usr \
                            --docdir=/usr/share/doc/pcre \
                            --enable-utf \
                            --enable-unicode-properties \
                            --enable-pcregrep-libz \
                            --enable-pcregrep-libbz2")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
