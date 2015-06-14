
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def build():
    autotools.make ()

def install():
    autotools.install()
    pisitools.dosym("/usr/lib/libstfl.so.0.22", "/usr/lib/libstfl.so.0")
    pisitools.dodoc ("COPYING")
