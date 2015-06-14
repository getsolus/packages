
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os

def setup():
    shelltools.export("FORCE_UNSAFE_CONFIGURE", "1")
    # Fix glibc 2.17 issue
    os.system ("sed -i -e '/gets is a/d' gnu/stdio.in.h")
    autotools.configure ("--disable-static --libexecdir=/usr/sbin --bindir=/bin")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc("AUTHORS", "COPYING", "ChangeLog", "NEWS", "README", "THANKS")
