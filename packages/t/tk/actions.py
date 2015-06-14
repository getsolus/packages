
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.cd("unix")
    autotools.configure()

def build():
    shelltools.cd("unix")
    autotools.make()

def install():
    shelltools.cd("unix")
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
