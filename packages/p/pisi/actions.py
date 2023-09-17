from pisi.actionsapi import get, pisitools, shelltools, pythonmodules

def install():
    pythonmodules.install()

    pisitools.dosym("eopkg-cli", "/usr/bin/eopkg")
    pisitools.dosym("uneopkg", "/usr/bin/unpisi")
    pisitools.dosym("lseopkg", "/usr/bin/lspisi")
    pisitools.dodir("/etc/mudur")
    shelltools.echo("%s/etc/mudur/locale" % get.installDIR(), "")
