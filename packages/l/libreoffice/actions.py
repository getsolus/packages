#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools, shelltools

LoVersion = "5.0.1.2"

OurWorkDir = "%s/libreoffice-%s" % (get.workDIR(), LoVersion)

def presetup():
    # Because fucking *dash*
    shelltools.export("CONFIG_SHELL", "/bin/bash")
    ballpath = "%s/external/tarballs" % OurWorkDir
    if not shelltools.can_access_directory(ballpath):
        shelltools.makedirs(ballpath)

        for comp in [ "dictionaries", "help", "translations"]:
            name = "libreoffice-%s-%s.tar.xz" % (comp, LoVersion)
            shelltools.sym("../../../%s" % name, "%s/%s" % (ballpath, name))


    shelltools.chmod("%s/bin/unpack-sources" % OurWorkDir)
    shelltools.export("LO_PREFIX", "/usr")
    shelltools.cd(OurWorkDir)

def setup():
    presetup()

    confFlags = "--prefix=/usr      \
        --sysconfdir=/etc           \
        --with-vendor=\"Solus Operating System\" \
        --with-lang=ALL             \
        --with-help                 \
        --with-myspell-dicts        \
        --with-alloc=system         \
        --without-java              \
        --without-system-dicts      \
        --disable-gconf             \
        --disable-odk               \
        --disable-postgresql-sdbc   \
        --enable-release-build=yes  \
        --enable-python=system      \
        --with-system-boost         \
        --with-system-cairo         \
        --with-system-curl          \
        --with-system-expat         \
        --with-system-harfbuzz      \
        --with-system-icu           \
        --with-system-jpeg          \
        --with-system-lcms2         \
        --with-system-libpng        \
        --with-system-libxml        \
        --with-system-mesa-headers  \
        --with-system-nss           \
        --with-system-openssl       \
        --with-system-poppler       \
        --with-system-zlib          \
        --enable-gtk3               \
        --with-parallelism=%s" % (get.makeJOBS().replace("-j",""))
    shelltools.system("./autogen.sh %s" % confFlags)


def build():
    presetup()
    autotools.make("build-nocheck")


def install():
    presetup()
    autotools.rawInstall("distro-pack-install DESTDIR=%s" % get.installDIR())

    # Sometimes we have a missing ure-link. LibreOffice kinda gets annoyed.
    if not shelltools.can_access_file("%s/usr/lib/libreoffice/ure-link" % get.installDIR()):
        pisitools.dosym("/usr/lib/libreoffice/ure", "/usr/lib/libreoffice/ure-link")

    
