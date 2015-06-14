
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.configure ("--prefix=/usr \
                          --enable-shared \
                          --with-system-expat \
                          --with-system-ffi")
def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
    pisitools.remove ("/usr/bin/2to3")
