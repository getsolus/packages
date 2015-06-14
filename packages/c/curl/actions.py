
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    # Curl throws a hissy fit
    flags = get.CFLAGS().replace("-D_FORTIFY_SOURCE=2","")
    shelltools.export ("CFLAGS", flags)
    autotools.rawConfigure ("--prefix=/usr\
                             --disable-static\
                             --enable-threaded-resolver\
                             --without-gnutls \
                             --enable-libcurl-option \
                             --with-ca-bundle=/etc/ssl/certs/ca-certificates.crt")

def build():
    autotools.make ()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.dodoc ("docs/VERSIONS", "docs/MAIL-ETIQUETTE", "docs/BINDINGS", "docs/BUGS")
