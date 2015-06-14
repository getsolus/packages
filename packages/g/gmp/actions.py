
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools



def setup():
    autotools.configure ("--prefix=/usr --enable-cxx")

def build():
    autotools.make ()

def check():
    autotools.make ("check")

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

    # Add docs
    for doc in [ "isa_abi_headache", "configuration", "*.html"]:
        pisitools.dodoc ("doc/%s" % doc)
