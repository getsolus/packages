#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os

BuildDir = "nspr"

def setup():
    os.chdir (BuildDir)

    # Disable static libraries
    shelltools.system ("sed -i 's#$(LIBRARY) ##' config/rules.mk")

    autotools.configure ("--prefix=/usr\
                          --with-mozilla\
                          --with-pthreads \
                          --enable-64bit")

def build():
    os.chdir (BuildDir)
    autotools.make()

def install():
    os.chdir (BuildDir)
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Manully clean up some cruft we dont need
    pisitools.remove ("/usr/bin/prerr.properties")
    pisitools.remove ("/usr/bin/compile-et.pl")
