#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    pisitools.dosed ("etc/login.defs", "ENCRYPT_METHOD DES", "ENCRYPT_METHOD SHA512")
    pisitools.dosed ("etc/login.defs", "/var/spool/mail", "/var/mail")
    autotools.configure("--prefix=/usr --sysconfdir=/etc")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.remove ("/etc/login.defs")
    # Put passwd somewhere sensible
    pisitools.domove ("/usr/bin/passwd", "/bin/")
    # Get rid of groups
    for deletion in ["/usr/share/man/cs/man1/groups.1",\
                     "/usr/share/man/da/man1/groups.1",\
                     "/usr/share/man/de/man1/groups.1",\
                     "/usr/share/man/fr/man1/groups.1",\
                     "/usr/share/man/hu/man1/groups.1",\
                     "/usr/share/man/it/man1/groups.1",\
                     "/usr/share/man/ja/man1/groups.1",\
                     "/usr/share/man/ko/man1/groups.1",\
                     "/usr/share/man/man1/groups.1",\
                     "/usr/share/man/pl/man1/groups.1",\
                     "/usr/share/man/ru/man1/groups.1",\
                     "/usr/share/man/sv/man1/groups.1",\
                     "/usr/share/man/zh_CN/man1/groups.1",\
                     "/bin/groups"]:
        pisitools.remove (deletion)
