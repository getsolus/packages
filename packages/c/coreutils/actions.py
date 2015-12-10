#!/usr/bin/python

from pisi.actionsapi import shelltools, get, autotools, pisitools

movetobin = ["basename", "cat", "chgrp", "chmod", "chown", "cp", "cut", "date", "dd", "df",
             "dir", "echo", "env", "false", "link", "ln", "ls", "mkdir", "mknod", "mktemp", "mv",
             "nice", "pwd", "readlink", "rm", "rmdir", "sleep", "sort", "stty", "sync", "touch",
             "true", "uname", "unlink", "vdir"]

symtousrbin = ["env", "cut", "readlink"]

def setup():
    autotools.autoreconf("-vfi")
    shelltools.export ("FORCE_UNSAFE_CONFIGURE","1")
    autotools.configure ("--prefix=/usr         \
        --libexecdir=/usr/lib \
        --enable-largefile \
        --enable-no-install-program=kill,uptime")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

# move critical files into /bin
    for f in movetobin:
        pisitools.domove("/usr/bin/%s" % f, "/bin/")

    for f in symtousrbin:
        pisitools.dosym("../../bin/%s" % f, "/usr/bin/%s" % f)

    pisitools.dodoc("AUTHORS", "ChangeLog*", "NEWS", "README*", "THANKS", "TODO")
