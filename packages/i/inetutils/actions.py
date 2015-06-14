#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools


def setup():
    # We'll use alternatives to logger/whois, and screw having telnetd or talkd.
    autotools.configure("--disable-logger \
                         --disable-whois \
                         --disable-servers")


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    pisitools.removeDir("/usr/libexec")
