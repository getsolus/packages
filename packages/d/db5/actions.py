
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os

BuildDir = "%s/db-5.3.21/build_unix" % get.workDIR()

def setup():
    os.chdir (BuildDir)
    os.system ("../dist/configure --prefix=/usr      \
              --enable-compat185 \
              --enable-dbm       \
              --disable-static   \
              --enable-cxx")

def build():
    os.chdir (BuildDir)
    autotools.make ()

def install():
    os.chdir (BuildDir)
    autotools.make ("DESTDIR=%s docdir=/usr/share/doc/db-5.3.21 install" % get.installDIR())
