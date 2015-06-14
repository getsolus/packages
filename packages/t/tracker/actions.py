
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

shelltools.export("HOME", get.workDIR())


def setup():
    # TODO: --enable-mp3, --enable-poppler --enable-playlist
    autotools.configure("--disable-static \
                         --enable-introspection \
                         --enable-journal \
                         --enable-gnome-keyring \
                         --enable-libsecret \
                         --enable-network-manager \
                         --enable-libexif \
                         --enable-exempi \
                         --enable-miner-fs \
                         --enable-miner-thunderbird \
                         --enable-miner-firefox \
                         --enable-nautilus-extension \
                         --enable-gdkpixbuf \
                         --enable-libgif \
                         --enable-libjpeg \
                         --enable-libtiff \
                         --enable-libpng \
                         --enable-libvorbis \
                         --enable-libflac \
                         --enable-text \
                         --enable-icon")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING")
