
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--prefix=/usr\
                          --exec-prefix=\
                          --libdir=/usr/lib\
                          --docdir=/usr/share/doc/procps-ng-3.3.10\
                          --disable-static\
                          --disable-skill\
                          --disable-kill")

def build():
    autotools.make ()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
