
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.system ("./config --prefix=/usr\
                        --openssldir=/etc/ssl\
                        shared\
                        zlib-dynamic")

def build():
    autotools.make ("-j1")

def install():
    autotools.rawInstall("INSTALL_PREFIX=%s MANDIR=/usr/share/man" % get.installDIR())
    # Move pkgconfig back into /usr/lib/pkgconfig
    pisitools.domove("/usr/lib64/pkgconfig", "/usr/lib")

    # openssl decided it needed more conflicts. and more man pages.
    pisitools.rename("/usr/share/man/man1/passwd.1", "passwd.openssl.1") # shadow conflict
    pisitools.rename("/usr/share/man/man3/threads.3", "threads.openssl.3") # perl-docs conflict
