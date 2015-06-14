
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.system ("sed -i -e 's/CFLAGS=\"-O -Wall/& -DNO_LCHMOD/' unix/Makefile")

def build():
    autotools.make ("-f unix/Makefile linux_noasm")

def install():
    autotools.install ()
    pisitools.domove ("/usr/man", "/usr/share")
    pisitools.dodoc ("LICENSE", "BUGS")
