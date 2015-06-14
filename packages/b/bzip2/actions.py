
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools


def setup():
    # We want to use this makefile per the LFS instructions,
    # as we want all of the tools linked to libbz2
    autotools.make ("-f Makefile-libbz2_so")
    autotools.make ("clean")

def build():
    autotools.make()

def install():
    autotools.make ("PREFIX=%s/usr install" % get.installDIR())

    # Move the libraries into /lib/
    pisitools.dolib ("libbz2*so*", "/lib")

    # Install a symlink in /usr/lib for compatibility
    pisitools.dosym ("/lib/libbz2.so.1.0", "/usr/lib/libbz2.so")

    # Move everything into /bin
    pisitools.domove ("/usr/bin/*", "/bin/")

    # Clean up empty directories
    pisitools.removeDir ("/usr/bin")

    # Move man directory into the correct location
    pisitools.domove ("/usr/man", "/usr/share/man")
