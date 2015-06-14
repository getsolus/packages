
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

WorkDir = "icu"

def setup():
    shelltools.cd("source")
    autotools.configure("--prefix=/usr")

def build():
    shelltools.cd("source")
    autotools.make()

def install():
    shelltools.cd("source")
    autotools.install()
