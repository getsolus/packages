
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    libdir = "/usr/lib64" if get.buildTYPE() != "emul32" else "/usr/lib32"
    autotools.configure ("--disable-static\
                          --disable-docs\
                          --libdir=%s\
                          --with-baseconfigdir=/usr/share/fonts \
                          --with-configdir=/usr/share/fonts/conf.d \
                          --docdir=/usr/share/doc/fontconfig-2.10.2" % libdir)

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
