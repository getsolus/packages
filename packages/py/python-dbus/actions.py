
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

py2dir = "py2build"
py3dir = "py3build"

def configure(pvers, flags):
    shelltools.system("PYTHON=%s ../configure %s" % (pvers, flags))

def setup():
    confFlags = "--prefix=/usr \
                 --docdir=/usr/share/doc/python-dbus"
    shelltools.makedirs(py2dir)
    shelltools.cd(py2dir)
    configure ("/usr/bin/python", confFlags)
    shelltools.cd("..")
    shelltools.makedirs(py3dir)
    shelltools.cd(py3dir)
    configure("/usr/bin/python3", confFlags)

def build():
    shelltools.cd(py2dir)
    autotools.make ()
    shelltools.cd("..")
    shelltools.cd(py3dir)

def install():
    shelltools.cd(py2dir)
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
    shelltools.cd("..")
    shelltools.cd(py3dir)
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
