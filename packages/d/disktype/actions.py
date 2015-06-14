#!/usr/bin/env python

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

def build():
    shelltools.export("CCACHE_DIR", "%s" % get.workDIR())
    autotools.make('CFLAGS="%s -fno-stack-protector -fno-strict-aliasing"' % get.CFLAGS())

def install():
    pisitools.dobin("disktype")
    pisitools.doman("disktype.1")
    pisitools.dodoc("README", "HISTORY", "TODO")
