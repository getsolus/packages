#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.configure("--disable-vv \
                         --disable-idn \
                         --disable-meanwhile \
                         --disable-gtkspell \
                         --disable-gstreamer \
                         --disable-schemas-install \
                         --disable-tcl \
                         --disable-avahi")

def build():
    autotools.make()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())
    pisitools.removeDir("/usr/lib/perl5")
