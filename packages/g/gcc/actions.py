#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools
import shutil
import glob
import os

BuildDir = "%s/%s" % ( get.workDIR(), "gcc-build")
GccDir = "../gcc-%s" % get.srcVERSION()

SupportDir = "%s/%s" % ( get.workDIR(), "PathSupport")

IgnoreAutodep = True

Triplet = "x86_64-solus-linux"

def noCcache():
    # Force disable ccache for local builds
    os.environ["PATH"] = "/bin:/usr/bin:/sbin:/usr/sbin"

def setup():
    noCcache()
    shelltools.makedirs (BuildDir)

    shelltools.cd (BuildDir)

    # Because GCC is a dope.
    cflags = "-march=x86-64 -mtune=generic -g1 -O3 -fstack-protector -Wl,-z -Wl,now -Wl,-z -Wl,relro -Wl,-z,max-page-size=0x1000"
    cxxflags = "-march=x86-64 -mtune=generic -g1 -O3 -Wl,-z -Wl,now -Wl,-z -Wl,relro -Wl,-z,max-page-size=0x1000"

    shelltools.export("CFLAGS", cflags)
    shelltools.export("CXXFLAGS", cxxflags)
    shelltools.export("CFLAGS_FOR_TARGET", cflags)
    shelltools.export("CC", "%s-gcc" % Triplet)
    shelltools.export("CXX", "%s-g++" % Triplet)

    # Configure GCC
    shelltools.system ("%s/configure \
                        --prefix=/usr \
                        --with-pkgversion='Solus' \
                        --libdir=/usr/lib64 \
                        --libexecdir=/usr/lib64 \
                        --with-system-zlib \
                        --enable-shared \
                        --enable-threads=posix \
                        --enable-__cxa_atexit \
                        --enable-plugin \
                        --enable-gold \
                        --enable-ld=default \
                        --enable-clocale=gnu \
                        --enable-multilib \
                        --with-multilib-list=m32,m64 \
                        --enable-lto \
                        --with-bugurl='https://dev.solus-project.com/' \
                        --with-arch_32=i686 \
                        --enable-linker-build-id  \
                        --build=%s \
                        --target=%s \
                        --enable-languages=c,c++,fortran" % (GccDir, Triplet, Triplet) )

    # Print the summary
    shelltools.system ("%s/contrib/test_summary" % GccDir)

def build():
    noCcache()
    shelltools.cd (BuildDir)
    autotools.make ( "profiledbootstrap" )

def install():
    noCcache()
    shelltools.cd (BuildDir)

    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
    # Linky linky
    pisitools.dosym ("/usr/bin/cpp", "/lib/cpp")
    pisitools.dosym ("/usr/bin/gcc", "/usr/bin/cc")

    crtfiles = ["libgcc.a", "crtbegin.o", "crtend.o", "crtbeginS.o", "crtendS.o"]
    for crt in crtfiles:
        pisitools.dosym("/usr/lib64/gcc/%s/%s/%s" % (Triplet, get.srcVERSION(), crt), "/usr/lib64/%s" % crt)
        pisitools.dosym("/usr/lib64/gcc/%s/%s/32/%s" % (Triplet, get.srcVERSION(), crt), "/usr/lib32/%s" % crt)

    # Ensure LTO will work properly.
    pisitools.dodir("/usr/lib64/bfd-plugins")
    pisitools.dosym("/usr/lib64/gcc/%s/%s/liblto_plugin.so" % (Triplet, get.srcVERSION()), "/usr/lib64/bfd-plugins/liblto_plugin.so")
