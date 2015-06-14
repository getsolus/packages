
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

IgnoreAutodep = True

def setup():
    pisitools.dosed("setup.py","ndbm_libs =.*","ndbm_libs = ['gdbm', 'gdbm_compat']")
    autotools.autoreconf ("-vfi")
    autotools.configure ("--prefix=/usr\
                          --enable-shared")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
