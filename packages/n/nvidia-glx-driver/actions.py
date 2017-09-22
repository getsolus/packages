#!/usr/bin/python
import os.path

NoStrip = ["/"]

from pisi.actionsapi import get, shelltools, pisitools, autotools, kerneltools
import commands

# Required... built in tandem with kernel update
kernel_trees = {
    "linux-lts": "4.9.51-48.lts",
    "linux-current": "4.12.14-21.current"
}

def setup():
    """ Extract the NVIDIA binary for each kernel tree and rename it each time
        to match the desired tree, to ensure we don't have them conflicting. """
    blob = "NVIDIA-Linux-x86_64-%s" % get.srcVERSION()
    for kernel in kernel_trees:
        shelltools.system("sh %s.run --extract-only" % blob)
        shelltools.move(blob, kernel)

def build():
    for kernel in kernel_trees:
        build_kernel(kernel)

def build_kernel(typename):
    version = kernel_trees[typename]
    olddir = os.getcwd()
    shelltools.cd(typename + "/kernel")
    autotools.make("\"SYSSRC=/lib64/modules/%s/build\" module" % version)
    shelltools.cd(olddir)

def install_kernel(typename):
    olddir = os.getcwd()
    version = kernel_trees[typename]

    kdir = "/lib64/modules/%s/kernel/drivers/video" % version
    # kernel portion, i.e. /lib/modules/3.19.7/kernel/drivers/video/nvidia.ko
    shelltools.cd(typename + "/kernel")
    modules = ["nvidia.ko", "nvidia-modeset.ko", "nvidia-drm.ko", "nvidia-uvm.ko"]
    for mod in modules:
        pisitools.dolib_a(mod, kdir)

    shelltools.cd(olddir)

def install_modalias(typename):
    """ install_modalias will generate modaliases for the given tree, which will
        only be linux-lts for now
    """
    olddir = os.getcwd()
    shelltools.cd(typename + "/kernel")

    # install modalias
    pisitools.dodir("/usr/share/doflicky/modaliases")
    modfile = "%s/usr/share/doflicky/modaliases/%s.modaliases" % (get.installDIR(), get.srcNAME())
    shelltools.system("sh -e ../../nvidia_supported nvidia %s ../README.txt nvidia/nv-kernel.o_binary > %s" %
                     (get.srcNAME(), modfile))

    shelltools.cd(olddir)

def link_install(lib, libdir='/usr/lib', abi='1', cdir='.'):
    ''' Install a library with necessary links '''
    pisitools.dolib("%s/%s.so.%s" % (cdir, lib, get.srcVERSION()), libdir)
    pisitools.dosym("%s/%s.so.%s" % (libdir, os.path.basename(lib), get.srcVERSION()), "%s/%s.so.%s" % (libdir, os.path.basename(lib), abi))
    pisitools.dosym("%s/%s.so.%s" % (libdir, os.path.basename(lib), abi), "%s/%s.so" % (libdir, os.path.basename(lib)))

def link_install_egl(lib, libdir='/usr/lib', abi='1', cdir='.'):
    ''' Install EGL '''
    pisitools.dolib("%s/%s.so.%s" % (cdir, lib, abi), libdir)
    pisitools.rename("%s/%s.so.%s" % (libdir, lib, abi), "%s.so.%s" % (lib, get.srcVERSION()))

    pisitools.dosym("%s/%s.so.%s" % (libdir, lib, get.srcVERSION()), "%s/%s.so.%s" % (libdir, os.path.basename(lib), abi))
    pisitools.dosym("%s/%s.so.%s" % (libdir, lib, abi), "%s/%s.so" % (libdir, os.path.basename(lib)))
        
def install():
    for kernel in kernel_trees:
        install_kernel(kernel)
    install_modalias("linux-lts")

    # glx portion, always build from the linux-lts tree
    shelltools.cd("linux-lts")
    pisitools.dolib("nvidia_drv.so", "/usr/lib/xorg/modules/drivers")

    # libGL replacement - conflicts
    libs = ["libGL", "libglx"]
    for lib in libs:
        abi = '2' if lib == "libGLESv2" else "1"
        link_install(lib, "/usr/lib/glx-provider/nvidia", abi)
        if lib != "libglx":
            link_install(lib, "/usr/lib32/glx-provider/nvidia", abi, cdir='32')

    # EGL = special..
    spec_libs = ["libEGL", "libGLESv1_CM", "libGLESv2"]
    for lib in spec_libs:
        abi = '2' if lib == "libGLESv2" else "1"
        link_install_egl(lib, "/usr/lib/glx-provider/nvidia", abi)
        link_install_egl(lib, "/usr/lib32/glx-provider/nvidia", abi, cdir='32')

    # multilib friendly
    libs = [
        "libcuda",
        "libEGL_nvidia",
        "libGLESv1_CM_nvidia",
        "libnvcuvid",
        "libnvidia-compiler",
        "libnvidia-eglcore",
        "libnvidia-encode",
        "libnvidia-fatbinaryloader",
        "libnvidia-fbc",
        "libnvidia-glcore",
        "libnvidia-glsi",
        "libnvidia-ifr",
        "libnvidia-ml",
        "libnvidia-opencl",
        "libnvidia-ptxjitcompiler",
    ]

    # native only
    native_libs = ["libnvidia-cfg",
                   "libnvidia-gtk2",
                   "libnvidia-gtk3",
                   "libnvidia-wfb"]

    # libGLX_nvidia.so.0
    link_install("libGLX_nvidia", abi='0')
    link_install("libGLX_nvidia", libdir='/usr/lib32', cdir='32', abi='0')

    # libGLESv2_nvidia.so.2
    link_install("libGLESv2_nvidia", abi='2')
    link_install("libGLESv2_nvidia", libdir='/usr/lib32', cdir='32', abi='2')

    for lib in libs:
        link_install(lib)
        link_install(lib, libdir='/usr/lib32', cdir='32')
    for lib in native_libs:
        link_install(lib)

    # nvidia wayland is a special case..
    pisitools.dolib("libnvidia-egl-wayland.so.1.0.1", "/usr/lib")

    # vdpau provider
    link_install("libvdpau_nvidia", "/usr/lib/vdpau")
    link_install("libvdpau_nvidia", "/usr/lib32/vdpau", cdir='32')

    # TLS
    link_install("tls/libnvidia-tls")
    link_install("tls/libnvidia-tls", libdir='/usr/lib32', cdir='32')

    # Required for everything.
    pisitools.dolib("libGLdispatch.so.0", "/usr/lib")
    pisitools.dolib("32/libGLdispatch.so.0", "/usr/lib32")

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
    # Vulkan
    pisitools.insinto("/usr/share/vulkan/icd.d", "10_nvidia*.json")

    # Blacklist nouveau
    pisitools.dodir("/usr/lib/modprobe.d")
    shelltools.echo("%s/usr/lib/modprobe.d/nvidia.conf" % get.installDIR(),
        "blacklist nouveau")
