#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools
import os
WorkDir = "llvm-%s.src" % get.srcVERSION()

IgnoreAutodep = True

def setup():
    if get.buildTYPE() != "emul32":
        if not shelltools.can_access_directory("tools/clang"):
            shelltools.system("tar xf ../cfe-%s.src.tar.xz -C tools" % get.srcVERSION())
            shelltools.move("tools/cfe-%s.src" % get.srcVERSION(), "tools/clang")
            
            di = os.getcwd()
            os.chdir("tools/clang")
            shelltools.system("patch -p1 < ../../0001-Use-usr-lib64-for-dynamic-linker.patch")
            shelltools.system("patch -p1 < ../../0002-Implement-Solus-s-default-toolchain-options.patch")
            os.chdir(di)

        if not shelltools.can_access_directory("projects/compiler-rt"):
            shelltools.system("tar xf ../compiler-rt-%s.src.tar.xz -C projects" % get.srcVERSION())
            shelltools.move("projects/compiler-rt-%s.src" % get.srcVERSION(), "projects/compiler-rt")
        

    shelltools.export("LD_LIBRARY_PATH", "%s/Release/lib/" % os.getcwd())

    host = get.HOST()
    version = "5.2.0" # GCC version

    paths = ["/usr/include/",
             "/usr/include/c++/%s" % version,
             "/usr/include/c++/%s/%s" % (version,host),
             "/usr/include/c++/%s/backward" % (version),
             "/usr/lib64/gcc/%s/%s/include" % (host,version),
             "/usr/local/include" ]

    if get.buildTYPE() == "emul32":
        shelltools.export("CC", "gcc -m32")
        shelltools.export("CXX", "g++ -m32")
        host = "i686-pc-linux-gnu"
        prefix = "/emul32"
        options = "-DLLVM_LIBDIR_SUFFIX=32  -DCMAKE_C_FLAGS:STRING=-m32 -DCMAKE_CXX_FLAGS:STRING=-m32 -DLLVM_TARGET_ARCH:STRING=i686 -DLLVM_DEFAULT_TARGET_TRIPLE=\"%s\"" % host
    else:
        shelltools.export("CC", "gcc")
        shelltools.export("CXX", "g++")
        host = get.HOST()
        prefix = "/usr"
        options = "-DLLVM_LIBDIR_SUFFIX=64  -DCMAKE_C_FLAGS:STRING=-m64 -DCMAKE_CXX_FLAGS:STRING=-m64 -DLLVM_TARGET_ARCH:STRING=x86_64 -DLLVM_DEFAULT_TARGET_TRIPLE=\"%s\"" % host

    if not shelltools.can_access_directory("lebuild"):
        shelltools.makedirs("lebuild")

    shelltools.cd("lebuild")
    shelltools.system("cmake .. \
                          -DCMAKE_BUILD_TYPE=Release \
                          -DCMAKE_INSTALL_PREFIX=%s \
                          %s \
                          -DENABLE_OPTIMIZED=ON \
                          -DLLVM_ENABLE_ASSERTIONS=OFF \
                          -DLLVM_ENABLE_FFI=ON \
                          -DLLVM_BUILD_DOCS=OFF \
                          -DBUILD_SHARED_LIBS=ON \
                          -DLLVM_INCLUDEDIR=/usr/include \
                          -DENABLE_SHARED=ON .." % (prefix, options))

def build():
    shelltools.cd("lebuild")
    autotools.make()

def install():
    shelltools.cd("lebuild")
    autotools.make("install DESTDIR=%s" % get.installDIR())

    # Fix permissions of the static files
    if get.buildTYPE() != "emul32":
        shelltools.chmod("%s/usr/lib64/*.a" % get.installDIR(), mode=0644)

        pisitools.dodir("/usr/lib64/clang-analyzer")

        for i in ["scan-view", "scan-build"]:
            shelltools.system("cp -Rv ../tools/clang/tools/%s %s/usr/lib64/clang-analyzer" % (i, get.installDIR()))
            shelltools.system("ln -sv /usr/lib64/clang-analyzer/%s/%s %s/usr/bin/%s" % (i, i, get.installDIR(), i))

        pisitools.dosym("/usr/bin/clang", "/usr/lib64/clang-analyzer/scan-build/clang")
        shelltools.system("mv %s/usr/include/llvm/Config/llvm-config.h %s/usr/include/llvm/Config/llvm-config-64.h" % (get.installDIR(), get.installDIR()))

    else:
        pisitools.domove("/emul32/lib32/", "/usr/")
        shelltools.system("cp -Rv \"%s/emul32/include/\" \"%s/usr/\"" % (get.installDIR(), get.installDIR()))
        shelltools.system("mv %s/usr/include/llvm/Config/llvm-config.h %s/usr/include/llvm/Config/llvm-config-32.h" % (get.installDIR(), get.installDIR()))
        pisitools.removeDir("/emul32")

        if shelltools.can_access_file("%s/usr/include/llvm/Config/llvm-config.h" % get.installDIR()):
            pisitools.remove("/usr/include/llvm/Config/llvm-config.h")
        shelltools.echo("%s/usr/include/llvm/Config/llvm-config.h" % get.installDIR(), """#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "llvm-config-32.h"
#elif __WORDSIZE == 64
#include "llvm-config-64.h"
#else
#error "Unknown word size"
#endif""")
