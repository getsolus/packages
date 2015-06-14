from pisi.actionsapi import get, pisitools, shelltools, pythonmodules

def install():
    pythonmodules.install()

    pisitools.dosym("pisi-cli", "/usr/bin/pisi")
    pisitools.dosym("pisi-cli", "/usr/bin/eopkg")
    pisitools.dodir("/etc/pisi")
    pisitools.dosym("/etc/eopkg/eopkg.conf", "/etc/pisi/pisi.conf")
    pisitools.dodir("/etc/mudur")
    shelltools.echo("%s/etc/mudur/locale" % get.installDIR(), "")
