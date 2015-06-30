
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

hookFile = "dhcpcd-hooks/50-dhcpcd-compat"

def setup():
    # We'll run from /run
    pisitools.dosed (hookFile, "/var/lib", "/run")
    autotools.configure ("--libexecdir=/lib/dhcpcd\
                          --dbdir=/run\
                          --sysconfdir=/etc\
                          --with-rootprefix=/ \
                          CFLAGS=\"-D_GNU_SOURCE %s\"" % get.CFLAGS())

def build():
    autotools.make ()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc ("README")

    pisitools.insinto ("/lib/dhcpcd/dhcpcd-hooks/", hookFile)
