#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools
import shutil
import glob
import os

BuildDir = "%s/%s" % ( get.workDIR(), "gcc-build")
GccDir = "../gcc-%s" % get.srcVERSION()

SupportDir = "%s/%s" % ( get.workDIR(), "PathSupport")

IgnoreAutodep = True

LegacyTriplet = "x86_64-evolveos-linux"
Triplet = "x86_64-solus-linux"

def get_host_gcc_version():
    return os.path.basename(glob.glob("/usr/lib64/gcc/*/*")[0])

def check_host():
    ''' To avoid a catastrophic build failure(+chain reaction), we trick the
        bootstrap by making the new triplet name already exist..

        Two things:
            Don't try this at home, kids!
            Symlinks are the magic that hold distributions together. Seriously.
    '''
    version = get_host_gcc_version()
    bins = ["%s-gcc" % Triplet,
            "%s-gcc-%s" % (Triplet, version),
            "%s-g++" % Triplet,
            "%s-c++" % Triplet,
            "%s-gcc-ar" % Triplet,
            "%s-gcc-nm" % Triplet,
            "%s-gcc-ranlib" % Triplet]
    if not os.path.exists(SupportDir):
        os.makedirs(SupportDir)
    for i in bins:
        if not os.path.exists(os.path.join("/usr/bin", i)):
            if not os.path.exists(os.path.join(SupportDir, i)):
                os.system("ln -sv /usr/bin/%s %s/%s" % (i.replace(Triplet,LegacyTriplet), SupportDir, i))
    if SupportDir not in os.environ['PATH']:
        os.environ['PATH'] = "%s:%s" % (SupportDir, os.environ['PATH'])

def setup():
    shelltools.makedirs (BuildDir)
    check_host()

    shelltools.cd (BuildDir)

    # Because GCC is a dope.
    cflags = get.CFLAGS().replace("-D_FORTIFY_SOURCE=2", "")
    cxxflags = get.CXXFLAGS().replace("-D_FORTIFY_SOURCE=2", "")

    shelltools.export("CFLAGS", cflags)
    shelltools.export("CXXFLAGS", cxxflags)
    shelltools.export("CC", "%s-gcc" % Triplet)
    shelltools.export("CXX", "%s-g++" % Triplet)

    # Configure GCC
    shelltools.system ("%s/configure \
                        --prefix=/usr \
                        --with-pkgversion='Solus Project' \
                        --libdir=/usr/lib64 \
                        --libexecdir=/usr/lib64 \
                        --with-system-zlib \
                        --enable-shared \
                        --enable-threads=posix \
                        --enable-__cxa_atexit \
                        --enable-plugin \
                        --disable-gold \
                        --enable-ld=default \
                        --enable-clocale=gnu \
                        --disable-multilib \
                        --enable-lto \
                        --with-bugurl='https://bugs.solus-project.com' \
                        --with-arch_32=i686 \
                        --enable-linker-build-id  \
                        --build=%s \
                        --target=%s \
                        --enable-languages=c,c++,fortran" % (GccDir, Triplet, Triplet) )

    # Print the summary
    shelltools.system ("%s/contrib/test_summary" % GccDir)

def build():
    check_host()
    shelltools.cd (BuildDir)
    autotools.make ()

def install():
    check_host()
    shelltools.cd (BuildDir)

    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
    # Linky linky
    pisitools.dosym ("/usr/bin/cpp", "/lib/cpp")
    pisitools.dosym ("/usr/bin/gcc", "/usr/bin/cc")

    crtfiles = ["libgcc.a", "crtbegin.o", "crtend.o", "crtbeginS.o", "crtendS.o"]
    for crt in crtfiles:
        pisitools.dosym("/usr/lib64/gcc/%s/%s/%s" % (get.HOST(), get.srcVERSION(), crt), "/usr/lib64/%s" % crt)
