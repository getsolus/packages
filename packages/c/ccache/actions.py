
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--disable-static")

def build():
    autotools.make()

def install():
    autotools.install()
    pisitools.dodir("/usr/lib/ccache/bin")
    pisitools.dosym("/usr/bin/ccache", "/usr/lib/ccache/bin/gcc")
    pisitools.dosym("/usr/bin/ccache", "/usr/lib/ccache/bin/x86_64-evolveos-linux-gcc")
    pisitools.dosym("/usr/bin/ccache", "/usr/lib/ccache/bin/g++")
    pisitools.dosym("/usr/bin/ccache", "/usr/lib/ccache/bin/x86_64-evolveos-linux-g++")

