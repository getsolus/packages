
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def build():
    autotools.make()

def install():
    autotools.make("PREFIX=%s/usr install" % get.installDIR())

    # Put stuff into sbin and clean up
    pisitools.domove("/usr/sbin/*", "/sbin/")
    pisitools.removeDir("/usr/sbin")

    pisitools.dodoc("COPYING", "ChangeLog")
