
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

shelltools.export("HOME", get.workDIR())


def setup():
    autotools.configure("--disable-static \
                         --enable-glib \
                         --enable-cogl-pango \
                         --disable-cogl-gst \
                         --enable-gdk-pixbuf \
                         --enable-examples-install \
                         --enable-gles2 \
                         --enable-gl \
                         --enable-cogl-gles2 \
                         --enable-glx \
                         --enable-wayland-egl-platform \
                         --enable-kms-egl-platform \
                         --enable-wayland-egl-server \
                         --enable-xlib-egl-platform")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("ChangeLog", "COPYING")
