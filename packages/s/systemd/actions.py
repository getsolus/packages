#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
import shutil

# Avoid g-ir-scanner FTB/SV
shelltools.export ("HOME", get.installDIR())

# Circular deps  - woo
IgnoreAutodep = True

def setup():
    if get.buildTYPE() == "emul32":
        autotools.rawConfigure("--prefix=/usr \
                            --libdir=/usr/lib32 \
                            --disable-tests \
                            --disable-ima \
                            --disable-seccomp \
                            --disable-pam \
                            --disable-kmod \
                            --disable-networkd \
                            --enable-split-usr \
                            --disable-libiptc \
                            --disable-lz4 \
                            --disable-manpages \
                            --without-python \
                            --disable-selinux \
                            --enable-compat-libs \
                            --disable-myhostname \
                            --disable-libcurl \
                            --disable-libidn \
                            --disable-hostnamed \
                            --disable-libcryptsetup")
    else:
        autotools.configure ("--libexecdir=/usr/lib \
                          --localstatedir=/var  \
                          --sysconfdir=/etc \
                          --with-sysvinit-path=/etc/init.d \
                          --disable-networkd \
                          --disable-selinux \
                          --enable-compat-libs \
                          --with-pamlibdir=/lib/security \
                          --enable-split-usr \
                          --disable-terminal \
                          --enable-vconsole \
                          --disable-kdbus \
                          CFLAGS=\"%s -fno-lto\"" % get.CFLAGS())

def build():
    autotools.make ()

def install():
    idir = get.installDIR()
    # Force to subdirectory so we dont trash 64-bit installs
    if get.buildTYPE() == "emul32":
        idir += "/derpmcderp"

    autotools.rawInstall ("DESTDIR=%s" % idir)

    bdir = os.path.join(get.installDIR(), ".cache")
    if os.path.exists(bdir):
        shutil.rmtree(bdir)

    if get.buildTYPE() == "emul32":
        pisitools.dodir("/usr")
        shelltools.system("mv \"%s/usr/lib32\" \"%s/usr/.\"" % (idir, get.installDIR()))
        shutil.rmtree(idir)
        # udev compatibility stuff
        pisitools.dosym ("/usr/lib32/libudev.so", "/usr/lib32/libudev.so.0")
        return

    # udev compatibility stuff
    pisitools.dosym ("/usr/lib/libudev.so", "/usr/lib/libudev.so.0")

    pisitools.dosym ("/usr/bin/udevadm", "/sbin/udevadm")
    pisitools.dosym ("/usr/lib/systemd/systemd-udevd", "/lib/udev/udevd")

    # Final tweaks ^^
    pisitools.dosym ("/usr/lib/systemd/systemd", "/bin/systemd")
    pisitools.dosym ("/usr/lib/systemd/systemd", "/sbin/init")

    # Make the journal directory
    pisitools.dodir ("/var/log/journal")

    # Install controll symlinks
    for control_item in ["reboot", "shutdown", "poweroff", "halt"]:
        pisitools.dosym ("/usr/bin/systemctl", "/sbin/%s" % control_item)

    # Remove unwanted rpm macro
    pisitools.removeDir ("/usr/lib/rpm")

    # We do not use nsswitch.conf - so don't break our networking.
    pisitools.remove("/usr/share/factory/etc/nsswitch.conf")
