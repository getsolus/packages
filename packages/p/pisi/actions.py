from pisi.actionsapi import get, pisitools, shelltools, pythonmodules

def install():
    pythonmodules.install()

    # BEGIN comment these out for the epoch bump build of pisi
    # pisitools.dosym("eopkg.bin", "/usr/bin/eopkg")
    # pisitools.dosym("eopkg.bin", "/usr/bin/eopkg-cli")
    # pisitools.dosym("lseopkg.py3", "/usr/bin/lseopkg")
    # pisitools.dosym("lseopkg.py3", "/usr/bin/lspisi.py2")
    # pisitools.dosym("uneopkg.py3", "/usr/bin/uneopkg")
    # pisitools.dosym("uneopkg.py3", "/usr/bin/unpisi.py2")
    # END comment these out for the epoch bump build of pisi
    pisitools.dodir("/etc/mudur")
    shelltools.echo("%s/etc/mudur/locale" % get.installDIR(), "")

    # Everything below here _removes_ stuff that we don't want installed.
    # After the epoch bump, the goal is to make pisi own as little as
    # practically possible, so that eopkg4 can own it instead for
    # co-installability purposes as we deprecate pisi.
    #
    # Uncomment the line below for the epoch bump build of pisi
    shelltools.unlinkDir("%s/usr/share/defaults" % get.installDIR())
    pisitools.remove("/usr/share/doc/pisi/dependency.pdf")
    pisitools.remove("/usr/share/doc/pisi/package_versions.pdf")
