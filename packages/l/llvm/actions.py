#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
WorkDir = "llvm-%s.src" % get.srcVERSION()

IgnoreAutodep = True

def setup():
    if not shelltools.can_access_directory("tools/clang"):
        shelltools.system("tar xf ../cfe-%s.src.tar.xz -C tools" % get.srcVERSION())
        shelltools.move("tools/cfe-%s.src" % get.srcVERSION(), "tools/clang")
    if not shelltools.can_access_directory("projects/compiler-rt"):
        shelltools.system("tar xf ../compiler-rt-%s.src.tar.xz -C projects" % get.srcVERSION())
        shelltools.move("projects/compiler-rt-%s.src" % get.srcVERSION(), "projects/compiler-rt")

    shelltools.export("LD_LIBRARY_PATH", "%s/Release/lib/" % os.getcwd())

    shelltools.export("CC", "gcc")
    shelltools.export("CXX", "g++")
    autotools.rawConfigure("--prefix=/usr              \
                            --sysconfdir=/etc          \
                            --libdir=/usr/lib/llvm     \
                            --enable-libffi            \
                            --enable-optimized         \
                            --enable-shared            \
                            --disable-assertions       \
                            --disable-debug-runtime    \
                            --host=%s \
                            --build=%s \
                            --with-gcc-toolchain=/usr \
                            --disable-expensive-checks" % (get.HOST(), get.HOST()))

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Fix permissions of the static files
    shelltools.chmod("%s/usr/lib/*.a" % get.installDIR(), mode=0644)

    pisitools.domove("/usr/docs", "/usr/share/", "doc")
