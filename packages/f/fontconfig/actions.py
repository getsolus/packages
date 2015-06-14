
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--prefix=/usr\
                          --disable-static\
                          --disable-docs\
                          --docdir=/usr/share/doc/fontconfig-2.10.2")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
