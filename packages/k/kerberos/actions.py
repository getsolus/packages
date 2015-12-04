#!/usr/bin/python


from pisi.actionsapi import autotools, get, shelltools, pisitools
import os

WorkDir = "."

SourceDist = "krb5-1.14.tar.gz"

BuildDir = "%s/krb5-1.14/src" % get.workDIR()

def setup():
    print "Extracting source"
    os.system("tar xf %s" % SourceDist)

    os.chdir(BuildDir)
    autotools.configure("--enable-dns-for-realm --with-system-es --with-system-et")

def build():
    os.chdir(BuildDir)
    autotools.make("-j1")

def install():
    os.chdir(BuildDir)
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Fix library permissions
    for library in ["gssapi_krb5", "gssrpc", "k5crypto", "kadm5clnt_mit", \
                    "kdb5", "krb5", "krb5support", "verto"]:
        shelltools.chmod("%s/usr/lib/lib%s.so*" %(get.installDIR(), library), mode=0755)
