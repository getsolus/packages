
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.rawConfigure ("--prefix=/usr\
                             --sysconfdir=/etc")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
    pisitools.removeDir("/usr/lib/dracut/modules.d/00dash")
    pisitools.removeDir("/usr/lib/dracut/modules.d/00bootchart")
    pisitools.removeDir("/usr/lib/dracut/modules.d/02caps")
