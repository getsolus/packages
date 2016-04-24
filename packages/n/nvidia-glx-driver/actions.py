#!/usr/bin/python
import os.path

NoStrip = ["/"]

from pisi.actionsapi import get, shelltools, pisitools, autotools, kerneltools
import commands

wdir = "NVIDIA-Linux-x86_64-%s" % get.srcVERSION()

# Required... built in tandem with kernel update
kversion = "4.4.8"

def setup():
    shelltools.system("sh NVIDIA-Linux-x86_64-%s.run --extract-only" % get.srcVERSION())

def build():
    shelltools.cd(wdir + "/kernel")
    autotools.make("\"SYSSRC=/lib64/modules/%s/build\" module" % kversion)
    shelltools.cd("uvm")
    autotools.make("\"SYSSRC=/lib64/modules/%s/build\" module" % kversion)

def link_install(lib, libdir='/usr/lib', abi='1', cdir='.'):
    ''' Install a library with necessary links '''
    pisitools.dolib("%s/%s.so.%s" % (cdir, lib, get.srcVERSION()), libdir)
    pisitools.dosym("%s/%s.so.%s" % (libdir, lib, get.srcVERSION()), "%s/%s.so.%s" % (libdir, os.path.basename(lib), abi))
    pisitools.dosym("%s/%s.so.%s" % (libdir, lib, abi), "%s/%s.so" % (libdir, os.path.basename(lib)))
        
def install():
    # driver portion
    shelltools.cd(wdir)
    pisitools.dolib("nvidia_drv.so", "/usr/lib/xorg/modules/drivers")

    kdir = "/lib64/modules/%s/kernel/drivers/video" % kversion

    # libGL replacement - conflicts
    libs = ["libGL", "libEGL", "libGLESv1_CM", "libGLESv2", "libglx"]
    for lib in libs:
        abi = '2' if lib == "libGLESv2" else "1"
        link_install(lib, "/usr/lib/glx-provider/nvidia", abi)
        if lib != "libglx":
            link_install(lib, "/usr/lib32/glx-provider/nvidia", abi, cdir='32')

    # non-conflict libraries
    libs =  ["libnvidia-glcore", "libnvidia-eglcore", "libnvidia-glsi",
        "libnvidia-ifr", "libnvidia-fbc", "libnvidia-encode",
        "libnvidia-ml", "libcuda", "libnvcuvid", "libnvidia-opencl"]

    native_libs = ["libnvidia-cfg", "libnvidia-gtk2", "libnvidia-gtk3"]

    for lib in libs:
        link_install(lib)
        link_install(lib, libdir='/usr/lib32', cdir='32')
    for lib in native_libs:
        link_install(lib)

    # vdpau provider
    link_install("libvdpau_nvidia", "/usr/lib/vdpau")
    link_install("libvdpau_nvidia", "/usr/lib32/vdpau", cdir='32')

    # TLS
    link_install("tls/libnvidia-tls")
    link_install("tls/libnvidia-tls", libdir='/usr/lib32', cdir='32')

    # binaries
    bins = ["nvidia-debugdump", "nvidia-xconfig", "nvidia-settings",
        "nvidia-bug-report.sh", "nvidia-smi", "nvidia-modprobe",
        "nvidia-cuda-mps-control", "nvidia-cuda-mps-server",
        "nvidia-persistenced"]
    for bin in bins:
        pisitools.dobin(bin)

    # data files
    pisitools.dosed("nvidia-settings.desktop", "__UTILS_PATH__", "/usr/bin")
    pisitools.dosed("nvidia-settings.desktop", "__PIXMAP_PATH__", "/usr/share/pixmaps")
    pisitools.insinto("/usr/share/applications", "nvidia-settings.desktop")
    pisitools.insinto("/usr/share/pixmaps", "nvidia-settings.png")
    pisitools.insinto("/usr/share/OpenCL/vendors", "nvidia.icd")

    # kernel portion, i.e. /lib/modules/3.19.7/kernel/drivers/video/nvidia.ko
    shelltools.cd("kernel")
    pisitools.dolib_a("nvidia.ko", kdir)

    # install modalias
    pisitools.dodir("/usr/share/doflicky/modaliases")
    with open("%s/usr/share/doflicky/modaliases/%s.modaliases" % (get.installDIR(), get.srcNAME()), "w") as outp:
        inp = commands.getoutput("../../nvidia_supported nvidia %s ../README.txt nvidia.ko" % get.srcNAME())
        outp.write(inp)

    shelltools.cd("uvm")
    pisitools.dolib_a("nvidia-uvm.ko", kdir)

    # Blacklist nouveau
    pisitools.dodir("/usr/lib/modprobe.d")
    shelltools.echo("%s/usr/lib/modprobe.d/nvidia.conf" % get.installDIR(),
        "blacklist nouveau")
