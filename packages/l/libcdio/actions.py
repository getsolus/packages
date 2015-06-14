#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get
from pisi.actionsapi import shelltools

def setup():
    autotools.autoreconf("-vif")
    autotools.configure("--disable-static \
                         --with-cd-paranoia-name=libcdio-paranoia \
                         --disable-vcd-info \
                         --enable-cpp-progs \
                         --disable-rpath")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % (get.installDIR()))

    pisitools.dosed("%s/usr/include/cdio/version.h" % get.installDIR(), '%s[^"]+' % get.srcVERSION(), get.srcVERSION())
    pisitools.dosed("%s/usr/include/cdio/cdio_config.h" % get.installDIR(), "#define\s(CDIO_LIBCDIO_SOURCE_PATH).*", r"#undef \1")

    pisitools.dodoc("AUTHORS", "ChangeLog", "NEWS", "README", "THANKS")
