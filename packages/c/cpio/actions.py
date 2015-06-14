
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.system ("sed -i -e '/gets is a/d' gnu/stdio.in.h")
    autotools.configure("--prefix=/usr\
                         --bindir=/bin\
                         --libexecdir=/tmp\
                         --enable-mt\
                         --with-rmt=/usr/sbin/rmt")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
