from pisi.actionsapi import shelltools
from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get



def install():
    def do_chmod(path, mode):
        path = "%s/%s" %(get.installDIR(), path)
        shelltools.chmod(path, mode=mode)

    # Install everything
    pisitools.insinto("/", "*")

    for dire in ["/tmp", "/var/tmp", "/dev", "/usr/lib64", "/lib64", "/proc", "/sys", "/run/lock", "/root", "/home", "/run", "/media"]:
        pisitools.dodir(dire)

    # Adjust permissions
    do_chmod("/dev", 0755)
    do_chmod("/home", 0755)
    do_chmod("/media", 0755)
    do_chmod("/proc", 0555)
    do_chmod("/root", 0700)
    do_chmod("/run", 0755)
    do_chmod("/run/lock", 0775)
    do_chmod("/sys", 0755)
    do_chmod("/tmp", 01777)
    do_chmod("/usr/share/baselayout/shadow", 0600)
    do_chmod("/var/tmp", 01777)
    pisitools.dosym("../run", "/var/run")
    pisitools.dosym("../run/lock", "/var/lock")
    pisitools.dosym("lib64", "/lib")
    pisitools.dosym("lib64", "/usr/lib")

    pisitools.dosym("/proc/self/mounts", "/etc/mtab")

    # Write out a default .profile.. temporary
    shelltools.echo("%s/etc/skel/.profile" % get.installDIR(), "source /usr/share/defaults/etc/profile")
    shelltools.echo("%s/etc/skel/.bashrc" % get.installDIR(), "source /usr/share/defaults/etc/profile")

    # Remove legacy boot link
    pisitools.remove("/boot/boot")
