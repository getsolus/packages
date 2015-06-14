#!/usr/bin/python

from pisi.actionsapi import get, autotools, pisitools


def setup():
    # TODO:   gom-1.0: --enable-bookmarks
    autotools.configure("--disable-static \
                         --enable-goa \
                         --enable-filesystem \
                         --enable-jamendo \
                         --enable-flickr \
                         --enable-shoutcast \
                         --enable-apple-trailers \
                         --enable-magnatune \
                         --enable-youtube \
                         --enable-gravatar")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    
