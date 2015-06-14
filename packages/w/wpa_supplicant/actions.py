
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os

_workDir = "wpa_supplicant"

def build():
    os.chdir (_workDir)
    autotools.make ("BINDIR=/sbin LIBDIR=/lib PREFIX=/usr")

def install():
    os.chdir (_workDir)
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

    # Install D-BUS
    pisitools.insinto ("/usr/share/dbus-1/system-services", "dbus/*.service")
    pisitools.insinto ("/etc/dbus-1/system.d", "dbus/dbus-wpa_supplicant.conf")

    # Install systemd
    pisitools.insinto ("/usr/lib/systemd/system", "systemd/*.service")
