#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2005-2011 TUBITAK/UEAKE
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# Modified for use on SolusOS - Requires audit

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

import os

def linknonwide(targetDir):
    # symlink normal objects to widechar ones, to force widechar enabling
    for f in shelltools.ls("%s/%s/*w.*" % (get.installDIR(), targetDir)):
        source = shelltools.baseName(f)
        destination = source.replace("w.", ".")
        pisitools.dosym(source, "%s/%s" % (targetDir, destination))

def setup():
    configparams = "--without-debug \
--without-profile \
--disable-rpath \
--enable-const \
--enable-largefile \
--enable-widec \
--with-terminfo-dirs='/etc/terminfo:/usr/share/terminfo' \
--disable-termcap \
--enable-hard-tabs \
--enable-xmc-glitch \
--enable-colorfgbg \
--with-shared \
--with-rcs-ids \
--with-chtype='long' \
--with-mmask-t='long' \
--without-ada \
--enable-symlinks \
--without-gpm"

    autotools.configure(configparams)

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())


    libbasedir = "lib"
    # Handle static libs in /usr/%libdir/static
    pisitools.dodir("/usr/%s/static" % libbasedir)
    for i in shelltools.ls("%s/usr/%s/*.a" % (get.installDIR(), libbasedir)):
        pisitools.domove("/usr/%s/%s" % (libbasedir, shelltools.baseName(i)), "/usr/%s/static/" % libbasedir)

    linknonwide("/usr/%s/static" % libbasedir)
    linknonwide("/usr/%s" % libbasedir)

    # We need the basic terminfo files in /etc
    terminfo = ["ansi", "console", "dumb", "linux", "rxvt", "screen", "sun", \
                "vt52", "vt100", "vt102", "vt200", "vt220", "xterm", "xterm-color", "xterm-xfree86"]

    # http://liste.pardus.org.tr/gelistirici/2011-October/057009.html
    for d in ("ncurses", "ncursesw"):
        pisitools.dodir("/usr/include/%s" % d)
        for h in shelltools.ls("%s/usr/include/*.h" % get.installDIR()):
            pisitools.dosym("../%s" % os.path.basename(h), "/usr/include/%s/%s" % (d, os.path.basename(h)))

    for f in terminfo:
        termfile = f[0] + "/" + f
        if shelltools.can_access_file("/usr/share/terminfo/%s" % termfile):
            pisitools.dodir("/etc/terminfo/%s" % f[0])
            pisitools.domove("/usr/share/terminfo/%s" % termfile, "/etc/terminfo/%s" % f[0])
            pisitools.dosym("../../../../etc/terminfo/%s/%s" % (f[0], f), "/usr/share/terminfo/%s/%s" % (f[0], f))

    # Maintain proper linking, whack ncurses into /lib/
    pisitools.domove ("/usr/lib/libncurses*.so*", "/lib/")
    pisitools.dosym("/lib/libncurses.so", "/lib/libcurses.so")
    pisitools.dosym("/lib/libncursesw.so", "/lib/libcursesw.so")
    pisitools.dodoc("ANNOUNCE", "NEWS", "README*", "TO-DO")
