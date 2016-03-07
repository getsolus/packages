
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.rawConfigure("--prefix=/usr \
                                                    --sysconfdir=/etc/ssh \
                                                    --datadir=/usr/share/sshd \
                                                    --with-md5-passwords \
                                                    --with-privsep-path=/var/lib/sshd")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodir("/var/lib/sshd")
    shelltools.chmod("%s/var/lib/sshd" % get.installDIR(), 0700)