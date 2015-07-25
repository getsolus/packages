
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


BuildDir = "%s/%s" % ( get.workDIR(), "binutils-build")

def setup():
    # Don't install outdated standards.info
    shelltools.unlink ("etc/standards.info")
    shelltools.system ("sed -i.bak '/^INFO/s/standards.info //' etc/Makefile.in")
    shelltools.makedirs (BuildDir)

    shelltools.cd (BuildDir)
    # Configure
    shelltools.system ("../binutils-2.23.2/configure \
        --prefix=/usr \
        --enable-lto \
        --enable-multilib \
        --disable-gold \
        --disable-werror \
        --enable-plugins \
        --target=x86_64-solus-linux \
        --build=x86_64-solus-linux")

def build():
    shelltools.cd (BuildDir)
    autotools.make ("tooldir=/usr")

def install():
    shelltools.cd (BuildDir)
    autotools.rawInstall ("tooldir=/usr DESTDIR=%s" % get.installDIR())

    # Include the libiberty header
    pisitools.insinto ("/usr/include", "../binutils-2.23.2/include/libiberty.h")
