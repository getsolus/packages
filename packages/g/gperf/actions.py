
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--docdir=/usr/share/doc/gperf-3.0.4")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc ("AUTHORS", "ChangeLog", "COPYING")

    # Extra docs
    pisitools.dodoc ("doc/gperf.dvi", "doc/gperf.ps", "doc/gperf.pdf")
