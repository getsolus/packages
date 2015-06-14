
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    shelltools.system("./bootstrap.sh --prefix=%s/usr" % get.installDIR())

def build():
    shelltools.system("./b2 stage threading=multi link=shared")

def install():
    shelltools.system("./b2 install threading=multi link=shared")
