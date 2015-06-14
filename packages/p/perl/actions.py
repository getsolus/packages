
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.system ("sed -i -e \"s|BUILD_ZLIB\s*= True|BUILD_ZLIB = False|\"\
                        -e \"s|INCLUDE\s*= ./zlib-src|INCLUDE    = /usr/include|\" \
                        -e \"s|LIB\s*= ./zlib-src|LIB        = /usr/lib|\"         \
                        cpan/Compress-Raw-Zlib/config.in")

    shelltools.system ("./Configure -des -Dprefix=/usr\
                       -Dvendorprefix=/usr           \
                       -Dman1dir=/usr/share/man/man1 \
                       -Dman3dir=/usr/share/man/man3 \
                       -Dpager=\"/usr/bin/less -isR\"  \
                       -Duseshrplib")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
