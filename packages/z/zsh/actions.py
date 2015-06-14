
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--enable-pcre \
                                             --bindir=/bin \
                                             --with-tcsetpgrp")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc ("NEWS", "ChangeLog")
    pisitools.removeDir("/usr/share/zsh/site-functions")
