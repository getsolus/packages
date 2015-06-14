#!/usr/bin/python


from pisi.actionsapi import pythonmodules, pisitools, shelltools, get


def build():
    pythonmodules.compile()


def install():
    pythonmodules.install()

    # Copy in our data files
    pisitools.insinto("/usr/share/os-installer", "data/*")

    # Change log
    pisitools.insinto("/usr/share/os-installer", "changes")

    # Icons
    pisitools.insinto("/usr/share/icons/gnome/scalable/actions", "dist/icons/*")

    # Desktop file
    pisitools.insinto("/usr/share/applications", "dist/os-installer.desktop")
    pisitools.insinto("/etc/skel/Desktop", "dist/os-installer.desktop")
    shelltools.chmod("%s/etc/skel/Desktop/os-installer.desktop" % get.installDIR())

    # Configuration file
    pisitools.insinto("/etc/os-installer", "dist/install.conf")

    # PolicyKit conf
    pisitools.insinto("/usr/share/polkit-1/actions", "dist/*.policy")

    pisitools.dobin("dist/os-installer-wrapper")
