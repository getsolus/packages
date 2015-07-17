
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import os

def setup():
    del os.environ["LD_AS_NEEDED"]
    autotools.autoreconf ("-fi")

    #disabled r300,r600,radeonsi
    autotools.configure ("--prefix=/usr                  \
                          --sysconfdir=/etc              \
                          --enable-texture-float         \
                          --enable-gles1                 \
                          --enable-gles2                 \
                          --enable-osmesa                \
                          --enable-xa                    \
                          --enable-gbm                   \
                          --enable-gallium-egl           \
                          --enable-gallium-gbm           \
                          --enable-glx-tls               \
                          --with-llvm-shared-libs        \
                          --enable-shared-glapi \
                          --with-egl-platforms=\"drm,x11,wayland\" \
                          --with-gallium-drivers=\"nouveau,r300,r600,radeonsi,svga,swrast\" ")

def build():
    autotools.make ()

    # Build the demos too
    autotools.make ("-C xdemos DEMOS_PREFIX=/usr")

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

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
    pisitools.dodir("/usr/lib/glx-provider/default")

    def redo_lib(name, version, short_version):
        ''' Move full version and short version '''
        pisitools.domove("/usr/lib/%s.so.%s" % (name, version), "/usr/lib/glx-provider/default/")
        pisitools.remove("/usr/lib/%s.so.%s" % (name, short_version))
        pisitools.remove("/usr/lib/%s.so" % name)
        # Reset non-versioned to short versioned - which is controlled by gl-driver-switch.
        pisitools.dosym("/usr/lib/%s.so.%s" % (name, short_version), "/usr/lib/%s.so" % name)
        pisitools.dosym("/usr/lib/glx-provider/default/%s.so.%s" % (name,version), "/usr/lib/glx-provider/default/%s.so.%s" % (name, short_version))
        pisitools.dosym("/usr/lib/glx-provider/default/%s.so.%s" % (name, version), "/usr/lib/glx-provider/default/%s.so" % name)

    redo_lib("libEGL", "1.0.0", "1")
    redo_lib("libGL", "1.2.0", "1")
    redo_lib("libGLESv1_CM", "1.1.0", "1")
    redo_lib("libGLESv2", "2.0.0", "2")
