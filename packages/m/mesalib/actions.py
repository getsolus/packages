
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os

def setup():
    del os.environ["LD_AS_NEEDED"]

    if get.buildTYPE() == "emul32":
        libdir = "lib32"
        mlib = "--build=i686-pc-linux-gnu --host=i686-pc-linux-gnu --with-clang-libdir=/usr/lib32"
        prefix = "/emul32"
        shelltools.export("CC", "gcc -m32")
        shelltools.export("CXX", "g++ -m32")
        cflags = get.CFLAGS().replace("-march=x86-64", "-march=i686")
        shelltools.export("CFLAGS", cflags)
        cxxflags = get.CXXFLAGS().replace("-march=x86-64", "-march=i686")
        shelltools.export("CXXFLAGS", cxxflags)
    else:
        libdir = "lib64"
        mlib = ""
        prefix = "/usr"
    autotools.autoreconf ("-fi")

    #disabled r300,r600,radeonsi
    autotools.rawConfigure ("--prefix=%s                  \
                          --sysconfdir=/etc              \
                          --enable-texture-float         \
                          --enable-egl                   \
                          --enable-gles1                 \
                          --enable-gles2                 \
                          --enable-osmesa                \
                          --enable-vdpau                 \
                          --enable-xa                    \
                          --enable-gbm                   \
                          --enable-gallium-egl           \
                          --enable-gallium-gbm           \
                          --enable-glx-tls               \
                          --with-llvm-shared-libs        \
                          --libdir=/usr/%s               \
                          --enable-shared-glapi \
                          --with-egl-platforms=\"drm,x11,wayland\" \
                          --with-gallium-drivers=\"nouveau,r300,r600,radeonsi,svga,swrast\"\
                          --disable-dri3 %s" % (prefix, libdir, mlib))

def build():
    autotools.make ()
    # Build the demos too
    if get.buildTYPE() != "emul32":
        autotools.make ("-C xdemos DEMOS_PREFIX=/usr")

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

    if get.buildTYPE() != "emul32":
        autotools.rawInstall ("-C xdemos DEMOS_PREFIX=/usr DESTDIR=%s" % get.installDIR())

    # Add docs at some stage

    #/usr/lib/libEGL.so.1
    #/usr/lib/libEGL.so.1.0.0
    #/usr/lib/libGL.so.1
    #/usr/lib/libGL.so.1.2.0
    #/usr/lib/libGLESv1_CM.so.1
    #/usr/lib/libGLESv1_CM.so.1.1.0
    #/usr/lib/libGLESv2.so.2
    #/usr/lib/libGLESv2.so.2.0.0

    libdir = "lib64" if get.buildTYPE() != "emul32" else "lib32"
    pisitools.dodir("/usr/%s/glx-provider/default" % libdir)

    def redo_lib(name, version, short_version):
        ''' Move full version and short version '''
        pisitools.domove("/usr/%s/%s.so.%s" % (libdir, name, version), "/usr/%s/glx-provider/default/" % libdir)
        pisitools.remove("/usr/%s/%s.so.%s" % (libdir, name, short_version))
        pisitools.remove("/usr/%s/%s.so" % (libdir, name))
        # Reset non-versioned to short versioned - which is controlled by gl-driver-switch.
        pisitools.dosym("/usr/%s/%s.so.%s" % (libdir, name, short_version), "/usr/%s/%s.so" % (libdir, name))
        pisitools.dosym("/usr/%s/glx-provider/default/%s.so.%s" % (libdir, name,version), "/usr/%s/glx-provider/default/%s.so.%s" % (libdir, name, short_version))
        pisitools.dosym("/usr/%s/glx-provider/default/%s.so.%s" % (libdir, name, version), "/usr/%s/glx-provider/default/%s.so" % (libdir, name))

    # .la being a dick again
    pisitools.remove("/usr/%s/lib*.la" % libdir)
    pisitools.remove("/usr/%s/dri/*.la" % libdir)
    redo_lib("libEGL", "1.0.0", "1")
    redo_lib("libGL", "1.2.0", "1")
    redo_lib("libGLESv1_CM", "1.1.0", "1")
    redo_lib("libGLESv2", "2.0.0", "2")
