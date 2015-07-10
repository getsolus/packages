
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

shelltools.export("HOME", get.workDIR())

def setup():
    shelltools.system("sed -i -e 's:getgroups:lightdm_&:' tests/src/libsystem.c")

    autotools.configure("--enable-introspection \
                         --enable-liblightdm-gobject \
                         --disable-static \
                         --disable-tests \
                         --libexecdir=/usr/lib/lightdm \
                         --with-greeter-session=lightdm-gtk-greeter")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodir("/usr/lib/systemd/system/graphical.target.wants")
    pisitools.dosym("/usr/lib/systemd/system/lightdm.service", "/usr/lib/systemd/system/displaymanager.service")
    pisitools.dosym("/usr/lib/systemd/system/lightdm.service", "/usr/lib/systemd/system/graphical.target.wants/lightdm.service")
