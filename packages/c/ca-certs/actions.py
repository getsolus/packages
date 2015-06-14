
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

from pisi.actionsapi.shelltools import system

def build():
    system ("./build_certs.sh")

def install():
    pisitools.insinto ("/etc/ssl/certs", "certs/*.pem")
    pisitools.insinto ("/etc/ssl/certs", "BLFS-ca-bundle*.crt", "ca-certificates.crt")
