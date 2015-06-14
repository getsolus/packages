
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

def setup():
    autotools.autoconf()
    autotools.configure("--disable-rpath \
                         --enable-shared \
                         --enable-pthread\
                         --with-sitedir=/usr/lib/ruby/site_ruby")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
