
#!/usr/bin/python


from pisi.actionsapi import autotools, get, pisitools

def setup():
    autotools.configure ("--disable-static \
                          --enable-python-bindings \
                          --enable-pam \
                          --with-securedir=/lib/security")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc ("AUTHORS", "ChangeLog", "COPYING")
