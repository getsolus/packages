#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
WorkDir = "llvm-%s.src" % get.srcVERSION()

IgnoreAutodep = True

def setup():
    if not shelltools.can_access_directory("tools/clang"):
        shelltools.system("tar xf ../cfe-%s.src.tar.xz -C tools" % get.srcVERSION())
        shelltools.move("tools/cfe-%s.src" % get.srcVERSION(), "tools/clang")
        
        di = os.getcwd()
        os.chdir("tools/clang")
        shelltools.system("patch -p1 < ../../0001-Use-usr-lib64-for-dynamic-linker.patch")
        os.chdir(di)

    if not shelltools.can_access_directory("projects/compiler-rt"):
        shelltools.system("tar xf ../compiler-rt-%s.src.tar.xz -C projects" % get.srcVERSION())
        shelltools.move("projects/compiler-rt-%s.src" % get.srcVERSION(), "projects/compiler-rt")
        

    shelltools.export("LD_LIBRARY_PATH", "%s/Release/lib/" % os.getcwd())

    host = get.HOST()
    version = "4.9.2" # GCC version

    paths = ["/usr/include/",
             "/usr/include/c++/%s" % version,
             "/usr/include/c++/%s/%s" % (version,host),
             "/usr/include/c++/%s/backward" % (version),
             "/usr/lib64/gcc/%s/%s/include" % (host,version),
             "/usr/local/include" ]

    shelltools.export("CC", "gcc")
    shelltools.export("CXX", "g++")
    autotools.rawConfigure("--prefix=/usr              \
                            --sysconfdir=/etc          \
                            --libdir=/usr/lib64        \
                            --enable-libffi            \
                            --enable-optimized         \
                            --enable-shared            \
                            --disable-assertions       \
                            --host=%s \
                            --build=%s \
                            --disable-expensive-checks \
                            --with-c-include-dirs=%s" % (get.HOST(), get.HOST(), ":".join(paths)))

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Fix permissions of the static files
    shelltools.chmod("%s/usr/lib/*.a" % get.installDIR(), mode=0644)

    pisitools.domove("/usr/docs", "/usr/share/", "doc")
