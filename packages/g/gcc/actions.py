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

def setup():
    shelltools.makedirs (BuildDir)

    shelltools.cd (BuildDir)

    # Because GCC is a dope.
    cflags = get.CFLAGS().replace("-D_FORTIFY_SOURCE=2", "").replace("-fexceptions", "")
    cxxflags = get.CXXFLAGS().replace("-D_FORTIFY_SOURCE=2", "").replace("-fexceptions", "")

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
                        --enable-multilib \
                        --with-multilib-list=m32,m64 \
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
    shelltools.cd (BuildDir)
    autotools.make ()

def install():
    shelltools.cd (BuildDir)

    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
    # Linky linky
    pisitools.dosym ("/usr/bin/cpp", "/lib/cpp")
    pisitools.dosym ("/usr/bin/gcc", "/usr/bin/cc")

    crtfiles = ["libgcc.a", "crtbegin.o", "crtend.o", "crtbeginS.o", "crtendS.o"]
    for crt in crtfiles:
        pisitools.dosym("/usr/lib64/gcc/%s/%s/%s" % (Triplet, get.srcVERSION(), crt), "/usr/lib64/%s" % crt)
        pisitools.dosym("/usr/lib/gcc/%s/%s/%s/32" % (Triplet, get.srcVERSION(), crt), "/usr/lib32/%s" % crt)
