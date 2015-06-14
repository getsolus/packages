
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--prefix=/usr\
                                              --exec-prefix=\
                                              --bindir=/usr/bin                      \
                                              --with-xtlibdir=/lib/xtables           \
                                              --with-pkgconfigdir=/usr/lib/pkgconfig \
                                              --enable-libipq                        \
                                              --enable-devel")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
