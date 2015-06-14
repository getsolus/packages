
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    autotools.configure("--enable-emacs-keybinding \
                     --enable-vi-keybinding \
                     --enable-clipart \
                     --enable-templates \
                     --enable-gio \
                     --without-evolution-data-server \
                     --without-goffice")


def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc ("COPYING", "ChangeLog", "AUTHORS")
