
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


BuildDir = "%s/%s" % ( get.workDIR(), "binutils-build")

def setup():
    shelltools.system ("sed -i.bak '/^INFO/s/standards.info //' etc/Makefile.in")
    shelltools.makedirs (BuildDir)

    shelltools.cd (BuildDir)
    # Configure
    shelltools.system ("../binutils-%s/configure \
        --prefix=/usr \
        --enable-lto \
        --with-lib-path=\"/usr/lib64:/lib64:/usr/lib32:/lib32 \" \
        --enable-multilib \
        --disable-gold \
        --disable-werror \
        --enable-plugins \
        --enable-secureplt \
        --enable-64-bit-bfd \
        --target=x86_64-solus-linux \
        --build=x86_64-solus-linux" % get.srcVERSION())

def build():
    shelltools.cd (BuildDir)
    autotools.make ("tooldir=/usr")

def install():
    shelltools.cd (BuildDir)
    autotools.rawInstall ("tooldir=/usr DESTDIR=%s" % get.installDIR())

    # Include the libiberty header
    pisitools.insinto ("/usr/include", "../binutils-%s/include/libiberty.h" % get.srcVERSION())
