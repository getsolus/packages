
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    shelltools.copytree("%s/usr/local/bin" % get.installDIR(), "%s/usr/bin" % get.installDIR())
    pisitools.removeDir("/usr/local")
    pisitools.doman("dvtm.1")
    pisitools.dodoc ("LICENSE")
