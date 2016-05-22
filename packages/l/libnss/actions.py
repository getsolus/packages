
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools

BuildDir = "nss"
InstallDir = "dist"

WorkDir="%s-%s/" % (get.srcNAME().replace("lib",""), get.srcVERSION())

def build():
    if get.buildTYPE() == "emul32":
        shelltools.export("CC", "gcc -m32")
        shelltools.export("CXX", "g++ -m32")
    else:
        shelltools.export ("USE_64", "1")

    shelltools.cd (BuildDir)
    shelltools.export ("BUILD_OPT", "1")
    shelltools.export ("NSPR_INCLUDE_DIR", "/usr/include/nspr")
    shelltools.export ("USE_SYSTEM_ZLIB", "1")
    shelltools.export ("NSS_USE_SYSTEM_SQLITE", "1")

    autotools.make ("nss_build_all -j1")

def install():
    libdir = "/usr/lib"
    if get.buildTYPE() != "emul32":
        for binary in ["certutil", "modutil", "pk12util", "signtool", "ssltap", "nss-config"]:
            pisitools.insinto("/usr/bin","dist/Linux*/bin/%s" % binary, sym=False)

        # Headers
        for header in ["dist/private/nss/*.h","dist/public/nss/*.h"]:
            pisitools.insinto("/usr/include/nss", header, sym=False)

        # Drop executable bits from headers
        shelltools.chmod("%s/usr/include/nss/*.h" % get.installDIR(), mode=0644)
    else:
        libdir = "/usr/lib32"

    for lib in ["*.a","*.chk","*.so"]:
        pisitools.insinto("%s/nss" % libdir,"dist/Linux*/lib/%s" % lib, sym=False)

    # Install nss-config and nss.pc
    pisitools.insinto("%s/pkgconfig" % libdir, "dist/Linux*/lib/pkgconfig/nss.pc", sym=False)

    for lib in ["libcrmf.a", "libfreebl3.so", "libnssutil3.so", "libnss3.so", "libsmime3.so", "libnssckbi.so", \
                 "libsoftokn3.so", "libnssdbm3.so", "libssl3.so", "libnsssysinit.so"]:
        pisitools.dosym ("%s/nss/%s" % (libdir, lib), "%s/%s" % (libdir, lib))

