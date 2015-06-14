
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, cmaketools, pisitools

def setup():
    cmaketools.configure()

def build():
    cmaketools.make()

def install():
    cmaketools.install()

    pisitools.dodoc ("AUTHORS", "ChangeLog", "COPYING")
