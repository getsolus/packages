
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.rawConfigure ("--prefix=/usr\
                                                     --disable-documentation\
                                                     --sysconfdir=/etc")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
