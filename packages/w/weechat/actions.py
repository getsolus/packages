
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, pisitools, cmaketools


def setup():
    #pisitools.dosed("configure.in", "AM_CONFIG_HEADER", "AC_CONFIG_HEADERS")
    #pisitools.system("./autogen.sh")
    cmaketools.configure()

def build():
    cmaketools.make()

def install():
    cmaketools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc("AUTHORS", "COPYING", "ChangeLog", "NEWS", "README")
