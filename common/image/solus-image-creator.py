#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  solus-image-creator.py - hardcoded jumble of ISO spinniness
#
#  The plan is to seed other values from a config file, but right now we
#  need a working ISO generator..
#  
#  Copyright 2015 Ikey Doherty <ikey@solus-project.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#

import os
import sys
import traceback
import shutil
import subprocess
import shlex
from op_helpers import OpItem, get_op_items
import time
from configobj import ConfigObj
import version


_target = os.path.abspath(os.getcwd())
release = False

def check_call(cmd):
    return subprocess.check_call(shlex.split(cmd))

def get_work_dir():
    return os.path.abspath("./IMAGEROOT")

def get_deploy_dir():
    return os.path.join(get_work_dir(), "deploy")

def get_image_root():
    return os.path.join(get_work_dir(), "root")

def get_image_path():
    return os.path.join(get_deploy_dir(), "LiveOS", "rootfs.img")

def get_live_dir():
    return os.path.join(get_deploy_dir(), "LiveOS")

def get_squash_img():
    return os.path.join(get_deploy_dir(), "LiveOS", "squashfs.img")

def get_boot_dir():
    return os.path.join(get_deploy_dir(), "boot")

def get_isolinux_dir():
    return os.path.join(get_deploy_dir(), "isolinux")

def get_efi_path():
    return os.path.join(get_deploy_dir(), "efi.img")

def get_efi_root():
    return os.path.join(get_work_dir(), "efi")

def get_cache_source():
    return "/var/lib/evobuild/packages"

def get_cache_target():
    return os.path.join(get_image_root(), "var/cache/eopkg/packages")

imageversion = None
def get_image_version():
    global imageversion
    if imageversion is not None:
        return imageversion
    imageversion = version.get_image_version()
    return imageversion

def get_image_version_file():
    return os.path.join(get_image_root(), "etc", "image-version")

def get_nvr_dir():
    global _target
    return os.path.join(_target, "releases", get_image_version())

def get_asset_dir():
    ''' i.e. script dir for /image/ '''
    return os.path.abspath(os.path.dirname(__file__))

def get_nvr_script():
    return os.path.join(get_asset_dir(), "grab-nvr.py")

kernel_version = None

def get_kernel_version():
    global kernel_version

    if kernel_version is not None:
        return kernel_version
    ret = None
    try:
        r = os.listdir(os.path.join(get_image_root(), "lib", "modules"))
        ret = os.path.basename(r[0])
        kernel_version = ret
    except Exception, ex:
        print("Unable to discover kernel version: %s" % ex)
        clean_exit(1)
    return ret

def create_support_dirs():
    ''' Remove, and then recreate support dirs '''

    if os.path.exists(get_work_dir()):
        try:
            shutil.rmtree(get_work_dir())
        except Exception, ex:
            print "Unable to remove work dirs: %s" % ex
            clean_exit(1)

    try:
        os.makedirs(get_work_dir())
    except Exception, ex:
        print "Unable to create work dir: %s" % ex
        clean_exit(1)

    dirs = os.path.dirname(get_image_path())
    try:
        os.makedirs(dirs)
    except Exception, ex:
        print "Unable to construct image dir: %s" % ex
        clean_exit(1)

    if not os.path.exists(get_cache_source()):
        try:
            os.makedirs(get_cache_source())
        except Exception, ex:
            print("Unable to construct cache source: %s" % ex)
            clean_exit(1)

# Spot the C coder.
did_mount = False
root_mounted = False
efi_mounted = False

def clean_exit(code):
    ''' Try and ensure we cleanup... '''
    if did_mount:
        down_root()
    sys.exit(code)

def do_mount(source,target,type=None,opts=None,bind=False):
    ''' Mount source over target, using optional type and options '''
    global did_mount

    try:
        if type:
            type = "-t %s" % type
        else:
            type = ""
        if opts:
            opts = "-o %s" % opts
        else:
            opts = ""
        bindFlag = "--bind" if bind else ""
        if not os.path.exists(target):
            os.makedirs(target)
        # mount -o loop -t ext4 base.i
        ret = os.system("mount %s %s %s \"%s\" \"%s\"" % (opts,type,bindFlag, source,target))
        if ret != 0:
            print "Mount for %s->%s failed" % (source, target)
            return False
    except Exception, e:
        print "Execution of mount failed: %s" % e
        return False
    did_mount = True
    return True


def do_umount(point,force=False):
    ''' umount a given mountpoint, optionally with the --force flag '''
    try:
        cmd = "umount" if not force else "umount -f"
        ret = os.system("%s \"%s\"" % (cmd, point))
        if ret != 0:
            print "umount of %s failed" % point
            return False
    except Exception, e:
        print "Execution of umount failed: %s" % e
        return False
    return True
    
def down_root():
    ''' Down le roots '''
    global did_mount
    global root_mounted

    # Tear down dbus
    if root_mounted:
        if os.path.exists(os.path.join(get_image_root(), "var/run/dbus/pid")):
            with open(os.path.join(get_image_root(), "var/run/dbus/pid"), "r") as pid:
                p = pid.read().strip()
                print "Killing d-bus pid: %s" % p
                os.system("kill %s" % p)
                time.sleep(0.5)
                if os.path.exists(os.path.join("/proc", p)):
                    print "Force-killing d-bus pid: %s" % p
                    os.system("kill -9 %s" % p)
        else:
            print "%s does not exist.. ?" % os.path.join(get_image_root(), "var/run/dbus/pid")

    dev = False
    with open("/etc/mtab", "r") as mounts:
        for line in mounts.readlines():
            line = line.replace("\r","").replace("\n","").strip()
            fields = line.split()
            if fields[1].startswith(get_image_root()) and fields[1].strip() != get_image_root():
                if fields[1].endswith("/dev"):
                    dev = True
                else:
                    print "umounting %s" % fields[1]
                    do_umount(fields[1])
    if dev:
        print "Umounting bind-mount /dev"
        do_umount(os.path.join(get_image_root(), "dev"))

    if root_mounted:
        do_umount(get_image_root())
    if efi_mounted:
        do_umount(get_efi_root())
    did_mount = False


def create_image():
    ''' Construct main rootfs.img '''
    size = 4096
    cmd = "dd if=/dev/zero of=\"%s\" bs=1 count=0 seek=%sM" % (get_image_path(), size)
    try:
        ret = check_call(cmd)
    except Exception, ex:
        print("Unable to construct image: %s" % ex)
        clean_exit(1)
    if ret != 0:
        print("Non-zero exit code")
        clean_exit(1)
    cmd = "mkfs -t %s -F \"%s\"" % ("ext4", get_image_path())
    try:
        ret = check_call(cmd)
    except Exception, ex:
        print("Unable to format image: %s" % ex)
        clean_exit(1)
    if ret != 0:
        print("Non-zero exit code")
        clean_exit(1)

    try:
        check_call("tune2fs -c0 -i0 \"%s\"" % get_image_path())
    except Exception, e:
        print("Unable to tune2fs image: %s" % e)


def init_root():
    ''' Construct run links, etc '''
    try:
        os.makedirs("%s/run/lock" % get_image_root())
        os.makedirs("%s/var" % get_image_root())
        os.symlink("../run/lock", "%s/var/lock" % get_image_root())
        os.symlink("../run", "%s/var/run" % get_image_root())
    except Exception, ex:
        print("Unable to set up links for bootstrap: %s" % ex)
        clean_exit(1)

def run_chroot(cmd):
    ''' Run a command in the chroot '''
    try:
        ret = check_call("chroot \"%s\" %s" % (get_image_root(), cmd))
    except Exception, ex:
        print("Unable to run chroot: %s" % ex)
        clean_exit(1)
    if ret != 0:
        print("Non-zero exit code from chroot command: %s" % cmd)
        clean_exit(1)

def create_squash(compression):
    ''' Construct the squashfs wrapper. '''
    wdir = os.getcwd()
    try:
        os.chdir(get_live_dir())
        # ensures correct structure, and stops squashfs reading itself
        check_call("mksquashfs \"%s\" \"%s\" -keep-as-directory -comp %s" % (".", "../squashfs.img", compression))
        shutil.move("../squashfs.img", "squashfs.img")
        os.unlink("rootfs.img")
    except Exception, ex:
        print("Unable to create squashfs: %s" % ex)
        clean_exit(1)
    os.chdir(wdir)

def configure_root():
    ''' Initialise new system, with dbus configuration to configure pending.
        This bollocks is only needed because Solus isn't stateless yet.
    '''
    baselayout = os.path.join(get_image_root(), "usr/share/baselayout")
    target = os.path.join(get_image_root(), "etc")

    try:
        for item in os.listdir(baselayout):
            try:
                shutil.copy2(os.path.join(baselayout, item), os.path.join(target, item))
            except Exception,ex:
                print("Unable to configure_root: %s" % ex)
                clean_exit(1)
    except Exception, e:
        print("Fatal error in configure_root: %s" % ex)
        clean_exit(1)

    # set up dbus account
    dbus_id = 18
    dbus_name = "messagebus"
    dbus_desc = "D-Bus Message Daemon"

    run_chroot("groupadd -g %d %s" % (dbus_id, dbus_name))
    run_chroot("useradd -m -d /var/run/dbus -r -s /bin/false -u %d -g %d %s -c \"%s\"" % (dbus_id, dbus_id, dbus_name, dbus_desc))
    run_chroot("/sbin/ldconfig -X")
    
    # ensure hwdb is generated, otherwise slow-ass boot times.
    run_chroot("/usr/bin/udevadm hwdb --update")
    
    # lastly, update mtimes to stop systemd running units it doesn't need to
    run_chroot("touch /etc")


def configure_live_account():
    ''' Configure the live user account, i.e. passwordless, sudo fun '''

    # Create the default user account
    cmd = "useradd -m -s /bin/bash -c \"%s\" %s" % ("Live User", "live")
    run_chroot(cmd)

    # Set an empty password for live user
    run_chroot("/bin/bash --login -c \"%s\"" % ("echo 'live:' |chpasswd"))

    # Finally, add the user to the right groups
    cmd = "usermod -a -G %s %s" % ("sudo,audio,video,cdrom", "live")
    run_chroot(cmd)

    # Modify sudoers so that live user is not asked for a password
    sudoers = os.path.join(get_image_root(), "etc/sudoers")
    line = "%live ALL=(ALL) NOPASSWD:ALL"
    cmd = "echo \"%s\" >> /etc/sudoers" % line
    run_chroot("/bin/bash --login -c '%s'" % cmd)

    # skeleton files that /root/ is going to need.
    skeldir = os.path.join(get_image_root(), "etc", "skel")
    for i in os.listdir(skeldir):
        tgt = os.path.join(get_image_root(), "root", i)
        if not os.path.exists(tgt):
            try:
                shutil.copy(os.path.join(skeldir, i), tgt)
            except Exception, ex:
                print("Failed to install skeleton file: %s" % ex)

    # do not run initial setup for live-user!
    cdir = os.path.join(get_image_root(), "home/live/.config")
    if not os.path.exists(cdir):
        try:
            os.makedirs(cdir)
        except Exception, ex:
            print("Failed to create config dir")
    cmd = "echo \"yes\" >> /home/live/.config/gnome-initial-setup-done"
    run_chroot("/bin/bash --login -c '%s'" % cmd)
    # make sure live actually owns live
    cmd = "chown -R %s:%s /home/%s" % ("live","live","live")
    run_chroot("/bin/bash --login -c '%s'" % cmd)

    fname = "%s/var/lib/AccountsService/users/live" % get_image_root()
    fdir = os.path.dirname(fname)
    if not os.path.exists(fdir):
        try:
            os.makedirs(fdir)
        except Exception, ex:
            print("Unable to create directories for live config")

    with open(fname, "w") as fout:
        fout.write("""[User]
Language=en_US.utf8
XSession=budgie-desktop
SystemAccount=false
""")

    assets = os.path.dirname(os.path.abspath(__file__))
    try:
        if os.path.exists(os.path.join(get_image_root(), "etc/gdm")):
            shutil.copy(os.path.join(assets, "gdm.conf"), os.path.join(get_image_root(), "etc/gdm/custom.conf"))
    except Exception, ex:
        print("Unable to copy gdm.conf: %s" % e)




def configure_boot():
    ''' Configure dracut correctly, depmod, etc. '''
    kernel = get_kernel_version()
    run_chroot("/sbin/ldconfig")
    run_chroot("/sbin/depmod %s" % kernel)

    if not os.path.exists(get_boot_dir()):
        try:
            os.makedirs(get_boot_dir())
        except Exception, ex:
            print("Unable to create boot dir: %s" % ex)
            clean_exit(1)

    # If this looks evil, you're not wrong.
    cmd = "dracut --lz4 --no-hostonly-cmdline -N --kver \"%s\" --force --lz4 --add \"dmsquash-live systemd pollcdrom\" --add-drivers \"squashfs ext3 ext2 vfat msdos sr_mod sd_mod ehci_hcd uhci_hcd xhci_hcd xhci_pci ohci_hcd usb_storage usbhid dm_mod device-mapper ata_generic libata\" /live.initrd" % kernel
    run_chroot(cmd)
    try:
        dsrc = os.path.join(get_image_root(), "live.initrd")
        ddst = os.path.join(get_boot_dir(), "initrd.img")
        shutil.move(dsrc, ddst)
    except Exception, ex:
        print("Unable to install boot initrd: %s" % ex)
        clean_exit(1)

    try:
        ksrc = os.path.join(get_image_root(), "boot", "kernel-%s" % kernel)
        kdst = os.path.join(get_boot_dir(), "kernel")
        shutil.copy(ksrc, kdst)
    except Exception, ex:
        print("Unable to install boot kernel: %s" % ex)
        clean_exit(1)

def create_efi(title, name, label):
    ''' Create the eltorito boot image '''
    global efi_mounted

    if not os.path.exists(get_efi_root()):
        try:
            os.makedirs(get_efi_root())
        except Exception, ex:
            print("Unable to create EFI root: %s" % ex)
            clean_exit(1)

    # in future we **must** check kernel/initrd sizes..
    size = 30
    cmd = "dd if=/dev/zero of=\"%s\" bs=1 count=0 seek=%sM" % (get_efi_path(), size)
    try:
        ret = check_call(cmd)
    except Exception, ex:
        print("Unable to construct EFI image: %s" % ex)
        clean_exit(1)
    pass

    cmd = "mkfs -t vfat \"%s\"" % get_efi_path()
    try:
        r = check_call(cmd)
    except Exception, ex:
        print("Unable to format EFI image: %s" % ex)
        clean_exit(1)
    if r != 0:
        print("Abnormal exit code for mkfs.vfat")
        clean_exit(1)

    if not do_mount(get_efi_path(), get_efi_root(), type="vfat", opts="loop"):
        print("Unable to mount EFI image")
        clean_exit(1)
    efi_mounted = True

    try:
        os.system("goofiboot install --force --no-variables --path=%s" % get_efi_root())
    except Exception, ex:
        print("Failed to install goofiboot: %s" % ex)
        clean_exit(1)

    for i in ["kernel", "initrd.img"]:
        try:
            sp = os.path.join(get_boot_dir(), i)
            if i.endswith(".img"):
                i = i.split(".img")[0]
            target = os.path.join(get_efi_root(), i)
            shutil.copy(sp, target)
        except Exception, ex:
            print("Failed to install EFI boot file: %s" % ex)
            clean_exit(1)

    # Write UEFI config..
    try:
        # root loader config
        with open(os.path.join(get_efi_root(), "loader/loader.conf"), "w") as conf:
            conf.write("default solus\ntimeout 4\n")
        # Solus entry
        with open(os.path.join(get_efi_root(), "loader/entries/solus.conf"), "w") as conf:
            conf.write("""title %(TITLE)s
linux /kernel
initrd /initrd
options root=live:LABEL=%(DESC)s ro rd.live.image rd.luks=0 rd.md=0 rd.dm=0""" % { 'DESC' : label, 'TITLE': title})
    except Exception, ex:
        print("Unable to write goofiboot config: %s" % ex)
        clean_exit(1)

    try:
        check_call("sync")
    except:
        pass

    if not do_umount(get_efi_path()):
        print("Unable to umount root EFI!")
        clean_exit(1)
    efi_mounted = False

def create_isolinux_boot(title, name, label):
    ''' Set up the SYSLINUX/isolinux configuration '''

    requirements = ["vesamenu.c32", "isolinux.bin", "libutil.c32", "libcom32.c32", "ldlinux.c32", "vesa.c32"]
    if not os.path.exists(get_isolinux_dir()):
        try:
            os.makedirs(get_isolinux_dir())
        except Exception, ex:
            print("Unable to create boot dir: %s" % ex)
            clean_exit(1)

    for i in requirements:
        try:
            shutil.copy(os.path.join("/usr/lib/syslinux", i), os.path.join(get_isolinux_dir(), os.path.basename(i)))
        except Exception, ex:
            print("Unable to install isolinux file: %s" % ex)
            clean_exit(1)

    try:
        conf = os.path.join(get_isolinux_dir(), "isolinux.cfg")
        f = open(conf, "w")

        splash =  "menu background splash.png"
        splashPath = os.path.join(os.path.dirname(get_work_dir()), "splash.png")
        if not os.path.exists(splashPath):
            splash = ""
        else:
            try:
                shutil.copy(splashPath, os.path.join(get_isolinux_dir(), "splash.png"))
            except:
                splash = ""

        # TODO: Make this templated and configurable.. Move along, now.
        lines = """
ui vesamenu.c32
timeout 50
default live

menu title %(TITLE)s
%(SPLASH)s
menu color screen       37;40      #80ffffff #00000000 std
MENU COLOR border       30;44   #40ffffff #a0000000 std
MENU COLOR title        1;36;44 #ffffffff #a0000000 std
MENU COLOR sel          7;37;40 #e0ffffff #20ffffff all
MENU COLOR unsel        37;44   #50ffffff #a0000000 std
MENU COLOR help         37;40   #c0ffffff #a0000000 std
MENU COLOR timeout_msg  37;40   #80ffffff #00000000 std
MENU COLOR timeout      1;37;40 #c0ffffff #00000000 std
MENU COLOR msg07        37;40   #90ffffff #a0000000 std
MENU COLOR tabmsg       31;40   #ffDEDEDE #00000000 std
MENU HIDDEN
MENU HIDDENROW 7
MENU WIDTH 78
MENU MARGIN 15
MENU ROWS 4
MENU VSHIFT 7
MENU TABMSGROW 11

label live
  menu label Start %(NAME)s
  kernel /boot/kernel
  append initrd=/boot/initrd.img root=live:LABEL=%(LABEL)s ro rd.live.image rd.luks=0 rd.md=0 rd.dm=0 --
menu default
label local
  menu label Boot from local drive
  localboot 0x80 
""" % { 'LABEL': label, 'TITLE': title, 'NAME' : name, 'SPLASH': splash }
        f.write(lines)
        f.close()
    except Exception, ex:
        print("Unable to write isolinux.cfg: %s" % ex)
        clean_exit(1)

def spin_iso(filename, label):
    wd = os.getcwd()
    isofile = os.path.join(wd, "SolusLive.iso")

    # Validation command:
    #xorriso -as mkisofs -U -A "SolusLive" -V "SolusLive" \
    #-volset "SolusLive" -J -joliet-long -r -v -T -x ./lost+found \
    #-isohybrid-mbr /usr/lib/syslinux/isohdpfx.bin \
    #-o ../../Solus-Daily.iso \
    #-b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 \
    #-boot-info-table \
    #-eltorito-alt-boot \
    #-e efi.img -no-emul-boot 
    try:
        cmd = """xorriso -as mkisofs -U -A "%(DESC)s" -V "%(DESC)s" \
    -volset "%(DESC)s" -J -joliet-long -r -v -T -x ./lost+found \
    -isohybrid-mbr /usr/lib/syslinux/isohdpfx.bin \
    -o %(ISOFILE)s \
    -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 \
    -boot-info-table \
    -eltorito-alt-boot -e efi.img -no-emul-boot  .""" % { 'DESC': label, 'ISOFILE': filename }
        os.chdir(get_deploy_dir())
        r = check_call(cmd)
        if r != 0:
            print("Image generation failed")
            clean_exit(1)
    except Exception, ex:
        print("Failed to spin_iso: %s" % ex)
        clean_exit(1)

    os.chdir(wd)

def main():
    ''' Main entry '''
    global root_mounted
    global release
    targetDirectory = get_image_root()

    if os.geteuid() != 0:
        print("Must be root to use image-creator")
        clean_exit(1)
    if not os.path.exists("image.conf"):
        print("image.conf does not exist - aborting")
        clean_exit(1)

    files = dict()
    files["/usr/bin/isohybrid"] = "syslinux"
    files["/usr/lib/goofiboot/goofibootx64.efi"] = "goofiboot"
    files["/usr/lib/syslinux/vesamenu.c32"] = "syslinux"
    files["/usr/bin/mksquashfs"] = "squashfs-tools"
    files["/usr/bin/xorriso"] = "libisoburn"

    bad = list()
    for k in files:
        if not os.path.exists(k):
            if files[k] not in bad:
                bad.append(files[k])
    if len(bad) > 0:
        print("Missing package(s): %s" % " ".join(bad))
        clean_exit(1)

    config = ConfigObj("image.conf")
    try:
        listfile = config["Image"]["Packages"]
        compression = config["Image"]["Compression"]
        label = config["Image"]["Label"]
        title = config["Image"]["Title"]
        name = config["Image"]["Name"]
        filename = config["Image"]["Filename"]
        release = bool(config["Image"]["Release"])
    except Exception, ex:
        print("Error parsing image.conf: %s" % ex)
        clean_exit(1)

    tfilename = filename
    filename = os.path.abspath(os.path.join(os.getcwd(), tfilename))
    op_list = None
    
    # optional.
    title = title.replace("##VERSION##", get_image_version())
    
    # Load package ops
    try:
        op_list = get_op_items(listfile)
    except Exception, ex:
        print("Failed to load packages: %s" % ex)
        clean_exit(1)

    # Ensure they listed a repo
    repos = [x for y in op_list for x in y if x.repo]
    if len(repos) == 0:
        print("Cannot continue without a repository definition")
        clean_exit(1)

    # cache the image version
    get_image_version()

    create_support_dirs()
    create_image()

    # Mount FS image
    if not do_mount(get_image_path(), get_image_root(), type="auto", opts="loop"):
        print("Unable to mount FS image")
        clean_exit(1)
    root_mounted = True

    init_root()

    if not os.path.exists(get_cache_target()):
        try:
            os.makedirs(get_cache_target())
        except Exception, ex:
            print("Unable to create cache target: %s" % ex)
            clean_exit(1)

    if not do_mount(get_cache_source(), get_cache_target(), bind=True):
        print("Unable to bind-mount cache")
        clean_exit(1)

    # Apply package ops
    for listage in op_list:
        if len(listage) > 1:
            head = listage[0]
            try:
                lines = head.batch(targetDirectory, listage)
                for line in lines:
                    try:
                        ret = check_call(line)
                    except Exception, ex:
                        print("Error executing package line: %s") % ex
                        clean_exit(1)
                    if ret != 0:
                        print("Non-zero exit: %s" % line)
                        clean_exit(1)
            except Exception, ex:
                print("Error executing operation: %s" % ex)
                clean_exit(1)
        else:
            op = listage[0]
            cmd = op.get_execute(targetDirectory)
            try:
                ret = check_call(cmd)
            except Exception, ex:
                print("Error executing package line: %s" % ex)
                clean_exit(1)
            if ret != 0:
                print("Non-zero exit: %s" % line)
                clean_exit(1)
        print "=== End stack ===\n"

    # need /dev/urandom for further usage of eopkg
    randr = os.path.join(get_image_root(), "dev/urandom")
    if not os.path.exists(randr):
        run_chroot("mknod -m 644 /dev/urandom c 1 9")
    configure_root()
    # TODO: Fix this chmod inside dbus itself.
    run_chroot("chmod o+x /usr/lib/dbus-1.0/dbus-daemon-launch-helper")
    run_chroot("dbus-daemon --system")
    # Shit ton of postinstalls. Can't wait till we're stateless.
    run_chroot("eopkg configure-pending")
    configure_live_account()

    # Enforce a locale, otherwise gnome-terminal is superbork
    localefile = os.path.join(get_image_root(), "etc", "locale.conf")
    try:
        with open(localefile, "w") as lfile:
            lfile.write("LANG=en_US.utf8\n")
    except Exception, ex:
        print("Failed to write locale: %s" % ex)
        clean_exit(1)

    # Here be hax: (TODO: Fix this in the packaging??)
    if os.path.exists(os.path.join(get_image_root(), "usr/sbin/NetworkManager")):
        run_chroot("systemctl enable NetworkManager")

    try:
        check_call("sync")
    except:
        pass

    # just get the kernel version cached while the medium is mounted..
    kvers = get_kernel_version()
    # set up dracut, pull out the initrd and kernel
    configure_boot()

    with open(get_image_version_file(), "w") as outw:
        outw.write(get_image_version() + "\n")

    # extract NVR
    if release:
        try:
            shutil.copy(get_nvr_script(), os.path.join(get_image_root(), "grab-nvr.py"))
            run_chroot("python /grab-nvr.py")
            os.unlink(os.path.join(get_image_root(), "grab-nvr.py"))
            for i in ["sources.nvr", "packages.nvr"]:
                endp = os.path.join(get_nvr_dir(), i)
                if not os.path.exists(get_nvr_dir()):
                    os.makedirs(get_nvr_dir())
                shutil.move(os.path.join(get_image_root(), i), endp)
        except Exception, ex:
            print("Failed to extract NVR files: %s" % ex)
    # Now ensure we have a clean image
    do_umount(get_cache_target())
    run_chroot("eopkg delete-cache")
    # Trick systemd into not running units it does not need to...
    run_chroot("/usr/bin/systemd-sysusers")
    run_chroot("touch /etc/.updated -r /usr")
    run_chroot("touch /var/.updated -r /usr")
    down_root()
    root_mounted = False

    # TODO: Check its actually ext :P
    try:
        check_call("e2fsck -y \"%s\"" % get_image_path())
        check_call("e2fsck -f \"%s\"" % get_image_path())
        check_call("resize2fs -M \"%s\"" % get_image_path())
    except Exception, e:
        print("Failed e2fsck - aborting")
        clean_exit(1)

    create_squash(compression)
    create_isolinux_boot(title, name, label)
    create_efi(title, name, label)
    spin_iso(filename, label)

    clean_exit(0)

    
if __name__ == "__main__":
    main()
