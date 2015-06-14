
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

WorkDir = "zip30"

def build():
    autotools.make ("-f unix/Makefile generic_gcc")

def install():
    for binary in [ "zip", "zipcloak", "zipnote", "zipsplit" ]:
        pisitools.dobin (binary)

    pisitools.dodoc ("LICENSE", "CHANGES", "README", "WHATSNEW")
