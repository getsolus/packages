#!/usr/bin/python


from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

def build():
    autotools.make('PREFIX=/usr \
                    OPT="%s"\
                    SHARED=yes \
                    ZLIB=no \
                    MANDIR=/usr/share/man \
                    SHAREDIR=/usr/share/hwids \
                    all'% get.CFLAGS())


def install():
    autotools.rawInstall('DESTDIR=%s \
                          SHARED=yes \
                          ZLIB=no \
                          MANDIR=/usr/share/man \
                          SHAREDIR=/usr/share/hwids \
                          install-lib \
                          install' % get.installDIR())

    pisitools.dodoc("COPYING","README")
