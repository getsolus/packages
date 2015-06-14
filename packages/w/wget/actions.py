
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure ("--with-ssl=openssl")

def build():
    autotools.make ()

def install():
    autotools.install ()

    pisitools.dodoc ("AUTHORS", "ChangeLog", "COPYING")

    shelltools.echo ("%s/etc/wgetrc" % get.installDIR(), "ca-directory=/etc/ssl/certs")
