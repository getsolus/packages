
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    # stack protector = boom, also with relro, fexceptions link issue
    shelltools.export("CFLAGS", "%s -fno-stack-protector" % get.CFLAGS().replace("-Wl,-z,now", "").replace("-fexceptions",""))
    shelltools.export("CXXFLAGS", "%s -fno-stack-protector" % get.CXXFLAGS().replace("-Wl,-z,now", "").replace("-fexceptions",""))
    autotools.configure()

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
