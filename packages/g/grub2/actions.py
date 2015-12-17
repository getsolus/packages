
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    shelltools.system ("sed -i -e '/gets is a/d' grub-core/gnulib/stdio.in.h")
    cflags = get.CFLAGS()
    cflags = cflags.replace("-fPIC", "") # clobbered asm issue (x86)
    cflags = cflags.replace("-fstack-protector-strong", "")
    shelltools.export ("CFLAGS", cflags)
    autotools.configure ("--prefix=/usr\
                                              --sysconfdir=/etc\
                                              --disable-werror")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
