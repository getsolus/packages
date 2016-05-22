
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
import shutil

def setup():
    libdir = "/usr/lib32" if get.buildTYPE() == "emul32" else "/usr/lib"
    autotools.aclocal("-I config-scripts")
    extOpts = ""
    if get.buildTYPE() == "emul32":
        extOpts = "--disable-avahi --disable-dnssd --disable-systemd"
    autotools.configure("--prefix=/usr \
                         --libdir=%s \
                         --without-rcdir \
                         --with-docdir=/usr/share/cups/doc \
                         --with-system-groups=lpadmin \
                         --enable-openssl \
                         --enable-systemd \
                         --enable-acl \
                         --enable-dbus \
                         --enable-libpaper %s" % (libdir, extOpts))

def build():
    autotools.make()

def install():
    idir = get.installDIR()
    # Force to subdirectory so we dont trash 64-bit installs
    if get.buildTYPE() == "emul32":
        idir += "/derpmcderp"

    autotools.rawInstall ("BUILDROOT=%s" % idir)

    if get.buildTYPE() == "emul32":
        pisitools.dodir("/usr")
        shelltools.system("mv \"%s/usr/lib32\" \"%s/usr/.\"" % (idir, get.installDIR()))
        shutil.rmtree(idir)
        return

    pisitools.dodir("/usr/lib/systemd/system/printer.target.wants")
    pisitools.dodir("/usr/lib/systemd/system/sockets.target.wants")
    pisitools.dodir("/usr/lib/systemd/system/multi-user.target.wants")

    pisitools.dosym("/usr/lib/systemd/system/org.cups.cupsd.service", "/usr/lib/systemd/system/printer.target.wants/org.cups.cupsd.service")
    pisitools.dosym("/usr/lib/systemd/system/org.cups.cupsd.socket", "/usr/lib/systemd/system/sockets.target.wants/org.cups.cupsd.socket")
    pisitools.dosym("/usr/lib/systemd/system/org.cups.cupsd.path", "/usr/lib/systemd/system/multi-user.target.wants/org.cups.cupsd.path")
