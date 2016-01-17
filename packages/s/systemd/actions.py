#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

# Avoid g-ir-scanner FTB/SV
shelltools.export ("HOME", get.installDIR())

# Circular deps  - woo
IgnoreAutodep = True

def setup():
    autotools.configure ("--libexecdir=/usr/lib \
                          --localstatedir=/var  \
                          --sysconfdir=/etc \
                          --with-sysvinit-path=/etc/init.d \
                          --disable-networkd \
                          --disable-selinux \
                          --enable-compat-libs \
                          --enable-split-usr \
                          --disable-terminal \
                          --enable-vconsole \
                          --disable-kdbus \
                          --with-pamlibdir=/lib/security \
                          CFLAGS=\"%s -fno-lto\"" % get.CFLAGS())

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

    # udev compatibility stuff
    pisitools.dosym ("/usr/bin/udevadm", "/sbin/udevadm")
    pisitools.dosym ("/usr/lib/systemd/systemd-udevd", "/lib/udev/udevd")
    pisitools.dosym ("/usr/lib/libudev.so", "/usr/lib/libudev.so.0")

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
