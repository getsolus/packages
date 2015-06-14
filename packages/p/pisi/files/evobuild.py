#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  evobuild.py
#  
#  Copyright 2015 Ikey Doherty <ikey@evolve-os.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.

import sys
import os
import shutil
import time
import glob
import xml.etree.ElementTree as ET
import fcntl
import argparse
import yaml
import pwd

BASEDIR = "/var/cache/evobuild"
INSTDIR = "/var/lib/evobuild/roots"
DLDIR = "/var/lib/evobuild/images"
PROFILE = "main-x86_64"

ARCHIVEDIR = "/var/lib/evobuild/archives"
ARCHIVEDIR_TGT = "/var/cache/eopkg/archives"


CCACHE_DIR = "/var/lib/evobuild/ccache"
CCACHE_TGT = "/root/.ccache"

PACKAGE_DIR = "/var/lib/evobuild/packages"
PACKAGE_TGT = "/var/cache/eopkg/packages"

IMG_URI = "https://www.solus-project.com/image_root/"
known_profiles = ["main-x86_64", "unstable-x86_64"]
IMG_SUFFIX = ".img"
IMG_DL_SUFFIX = ".img.xz"

# Lock file descriptor
lockfd = None
did_mount = False

update_mode = False

def config_path():
    ''' ypkg config path '''
    homeDir = os.path.expanduser("~")
    if "SUDO_UID" in os.environ:
        homeDir = pwd.getpwuid(int(os.environ['SUDO_UID'])).pw_dir
    confpath = os.path.join(homeDir, ".solus", "packager")
    if os.path.exists(confpath):
        return confpath
    return os.path.realpath(os.path.join(homeDir, ".evolveos", "packager"))


def work_dir():
    ''' Return workdir for overlayfs '''
    return os.path.realpath(os.path.join(BASEDIR, "work"))


def upper_dir():
    ''' Return upper_dir for overlayfs '''
    return os.path.realpath(os.path.join(BASEDIR, "transient"))


def lower_dir():
    ''' Return profiles lowerdir for overlayfs '''
    if update_mode:
        return os.path.realpath(os.path.join(INSTDIR, PROFILE))
    else:
        return os.path.realpath(os.path.join(BASEDIR, PROFILE))


def union_dir():
    ''' Return the union (overlayfs) mount point '''
    if update_mode:
        return lower_dir()
    else:
        return os.path.realpath(os.path.join(BASEDIR, "union"))


def archive_dir():
    ''' Return the archive mount point '''
    return os.path.realpath(os.path.join(union_dir(), ARCHIVEDIR_TGT[1:]))


def ccache_dir():
    ''' Return the ccache mount point '''
    return os.path.realpath(os.path.join(union_dir(), CCACHE_TGT[1:]))


def package_dir():
    ''' Return the package mount point '''
    return os.path.realpath(os.path.join(union_dir(), PACKAGE_TGT[1:]))


def image_path(dl=False):
    ''' Return path for the profile image '''
    return os.path.realpath(os.path.join(DLDIR, "%s%s" % (PROFILE, IMG_SUFFIX if not dl else IMG_DL_SUFFIX)))


def lock_file():
    ''' Current lock file '''
    if update_mode:
        return os.path.realpath(os.path.join(INSTDIR, "%s.lock" % PROFILE))
    else:
        return os.path.realpath(os.path.join(BASEDIR, "lock"))


def lock_root():
    ''' Lock the root and prevent concurrent manipulation '''
    global lockfd

    if os.path.exists(lock_file()):
        print "Lock file exists: %s" % lock_file()
        return False

    try:
        lockfd = open(lock_file(), "w")
        fcntl.lockf(lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lockfd.write("evobuild")
    except:
        return False
    return True


def unlock_root():
    ''' Unlock the root.. '''
    global lockfd

    if lockfd is not None:
        lockfd.close()
        try:
            if os.path.exists(lock_file()):
                os.unlink(lock_file())
        except Exception, e:
            print "Unable to clean lock file: %s" % lock_file()
            print e
            return False
        lockfd = None
    return True


def download_image():
    ''' Download the current profile image '''
    if os.path.exists(image_path(True)):
        return True
    if not os.path.exists(DLDIR):
        try:
            os.makedirs(DLDIR)
        except Exception, e:
            print "Unable to create directories: %s" % e
            return False

    uri = "%s%s%s" % (IMG_URI, PROFILE, IMG_DL_SUFFIX)
    cmd = "wget \"%s\" -O \"%s\"" % (uri, image_path(True))
    try:
        ret = os.system(cmd)
        if ret != 0:
            print "Invalid return code from wget. Aborting"
            if os.path.exists(image_path(True)):
                os.unlink(image_path(True))
            return False
    except Exception, e:
        print "Encountered error downloading image: %s" % e
        if os.path.exists(image_path(True)):
            os.unlink(image_path(True))
        return False
    return extract_image()


def do_mount(source,target,type=None,opts=None,bind=False):
    ''' Mount source over target, using optional type and options '''
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


def extract_image():
    ''' Extract the profile image... '''
    if os.path.exists(image_path()):
        return True
    print "Extracting image"
    cwd = os.getcwd()
    try:
        os.chdir(DLDIR)
        ret = os.system("unxz \"%s%s\"" % (PROFILE, IMG_DL_SUFFIX))
        if ret != 0:
            print "Invalid return code from unxz. Aborting"
            return False
    except Exception, e:
        print "Encountered error extracting image: %s" % e
        return False
    os.chdir(cwd)
    return True


def run_chroot(cmd):
    ''' Run a command in the chroot '''
    try:
        ret = os.system("chroot \"%s\" %s" % (union_dir(), cmd))
        if ret != 0:
            print "Return code was %s" % ret
            return False
    except Exception, e:
        print "Chroot exception: %s" % e
        return False
    return True

def get_pkgname(fname):
    if fname.endswith("pspec.xml"):
        try:
            tree = ET.parse(fname)
            root = tree.getroot()

            name = root.findall("Source/Name")[0].text
            return name
        except Exception, e:
            print "Invalid XML error: %s" % e
            clean_exit(1)
    else:
        y= None
        try:
            f = open(fname, "r")
            y = yaml.load(f)
        except Exception, e:
            print "Unable to load %s: %s" % (fname, e)
            clean_exit(1)
        if y is None:
            print "Error processing %s" % fname
            clean_exit(1)
        if "name" not in y:
            print "%s does not provide mandatory name token" % fname
            clean_exit(1)
        return y["name"]


def clean_exit(code):
    ''' Try and ensure we cleanup... '''
    if did_mount:
        down_root()
    unlock_root()
    sys.exit(code)


def main():
    ''' Le Main Entry.. '''
    global BASEDIR
    global INSTDIR
    global did_mount
    global PROFILE
    global update_mode

    pa = argparse.ArgumentParser(description="Build Evolve OS packages")
    pa.add_argument("init", nargs='?', help="Initialise the given profile")
    pa.add_argument("build", nargs='?', help="Build the specified source package")
    pa.add_argument("update",  nargs='?', help="Update a given chroot")
    pa.add_argument("-p", "--profile", type=str, help="Select a profile to build with")
    a = pa.parse_args()

    command = a.init
    what = a.build
    name = None

    if os.geteuid() != 0:
        print "This tool must be run as root. Aborting"
        clean_exit(1)


    if a.profile:
        if a.profile not in known_profiles:
            print "Unknown profile: %s" % a.profile
            print "Known profiles: %s" % ", ".join(known_profiles)
            clean_exit(1)
        else:
            PROFILE = a.profile
    else:
        PROFILE = "main-x86_64"

    if not command:
        print "Use one of init, build or update"
        clean_exit(1)

    supported_commands = ["build", "update", "init"]
    if command not in supported_commands:
        print "Unsupported operation: %s" % command
        clean_exit(1)

    if command == "build":
        if not what:
            print "Usage: %s build pspec.xml|package.yml" % sys.argv[0]
            clean_exit(1)
        if not os.path.exists(what):
            print "%s does not exist - aborting" % what
            clean_exit(1)
        elif not what.endswith("pspec.xml") and not what.endswith(".yml"):
            print "%s does not look like a valid source file. Aborting" % what
            clean_exit(1)

        # ypkg config file
        if not os.path.exists(config_path()):
            print "ypkg configuration file not present, aborting: %s" % config_path()
            clean_exit(1)

        name = get_pkgname(what)
        print "Building %s for %s" % (name, PROFILE)
        BASEDIR = os.path.join(BASEDIR, name)
    elif command == "update":
        if not os.path.exists(image_path()):
            print "Profile does not exist - did you forget to init?"
            clean_exit(1)
        update_mode = True
    elif command == "init":
        if not os.path.exists(image_path()):
            print "Obtaining lower profile image: %s" % image_path()
            if not download_image():
                print "Unable to obtain profile image. Aborting"
                clean_exit(1)
            print "Successfully initialised %s" % PROFILE
        else:
            print "%s is already initialised" % PROFILE
        clean_exit(0)

    # Make sure we never introduce a regression =)
    if PROFILE not in known_profiles:
        print "Unknown profile: %s" % PROFILE
        clean_exit(1)

    if not os.path.exists(BASEDIR):
        try:
            os.makedirs(BASEDIR)
        except Exception, e:
            print "Unable to create basedir: %s" % BASEDIR
            print e
            clean_exit(1)
    if update_mode and not os.path.exists(INSTDIR):
        try:
            os.makedirs(INSTDIR)
        except Exception, e:
            print "Unable to create instdir: %s" % INSTDIR
            print e
            clean_exit(1)

    if not lock_root():
        print "Unable to lock %s - aborting" % lock_file()
        clean_exit(1)


    create_support_dirs()

    # Check if our profile is present..
    if not os.path.exists(image_path()):
        print "Did you forget to init %s profile?" % PROFILE
        clean_exit(1)

    up_root()
    did_mount = True

    if not os.path.exists(os.path.join(union_dir(), "etc/localtime")):
        run_chroot("ln -sv /usr/share/zoneinfo/UTC /etc/localtime")

    # Attempt le dbus.
    if not run_chroot("dbus-daemon --system"):
        print "Warning: DBUS is not running!"

    if command == "build":
        if not copy_aux(what):
            print "Failure copying aux files.."
        else:
            do_update()
            cmd = "eopkg build -y /WORK/packages/pspec.xml -O /WORK" if what.endswith("pspec.xml") else "/bin/sh -c 'cd /WORK/; ypkg /WORK/packages/%s --force'" % os.path.basename(what)
            if run_chroot(cmd):
                print "Build successful"
                extract_build(what.endswith(".yml"))
            else:
                print "Build failed"
                clean_exit(-1)

    elif command == "update":
        do_update()

    down_root()
    clean_exit(0)

def do_update():
    ''' Ensures builders are up to date... '''
    if not run_chroot("eopkg upgrade -y"):
        print "Update failed"
    else:
        print "Update succeeded"
    if not run_chroot("eopkg it -c system.devel -y"):
        print "Devel update failed"
    else:
        print "Devel update complete"

def create_support_dirs():
    ''' Create required support directories '''
    # Purge old directories
    rms = [ work_dir(), upper_dir(), union_dir() ]
    for dir in rms:
        if os.path.exists(dir):
            try:
                shutil.rmtree(dir)
            except Exception, e:
                print "Unable to purge stagnant directory: %s" % dir
                print e
                clean_exit(1)

    # Test for cache enabling...
    if not os.path.exists(ARCHIVEDIR):
        try:
            os.makedirs(ARCHIVEDIR)
        except Exception, e:
            print "Unable to construct archive pool: %s" % ARCHIVEDIR
            print e
            clean_exit(1)
    # Test for ccache enabling...
    if not os.path.exists(CCACHE_DIR):
        try:
            os.makedirs(CCACHE_DIR)
        except Exception, e:
            print "Unable to construct ccache pool: %s" % CCACHE_DIR
            print e
            clean_exit(1)
    # Test for package caching..
    if not os.path.exists(PACKAGE_DIR):
        try:
            os.makedirs(PACKAGE_DIR)
        except Exception, e:
            print "Unable to construct package pool: %s" % PACKAGE_DIR
            print e
            clean_exit(1)

    # Construct new directories..
    for dir in rms:
        try:
            os.makedirs(dir)
        except Exception, e:
            print "Unable to make required directory: %s" % dir
            print e
            clean_exit(1)


def extract_build(yml=False):
    try:
        fs = glob.glob(os.path.join(union_dir(), "WORK", "*.eopkg"))
        for f in fs:
            shutil.copy2(f, os.path.join(os.getcwd(), os.path.basename(f)))
        if yml:
            fs = glob.glob(os.path.join(union_dir(), "WORK", "pspec_*.xml"))
            for f in fs:
                shutil.copy2(f, os.path.join(os.getcwd(), os.path.basename(f)))
    except Exception, e:
        print "Unable to extract file from build: %s" % e


def copy_aux(fname):
    dir = os.path.dirname(fname)
    try:
        os.makedirs(os.path.join(union_dir(), "WORK/packages"))
    except Exception, e:
        print "Unable to create work directory"
        return False
    pspec = fname.endswith("pspec.xml")
    target = os.path.join(union_dir(), "WORK/packages")

    files = None

    if pspec:
        files = ["actions.py", "pspec.xml"]
    else:
        # yaml
        files = [os.path.basename(fname)]
    try:
        for f in files:
            shutil.copyfile(os.path.join(dir, f), os.path.join(target, f))
    except Exception, e:
        print "Unable to copy aux file: %s" % e
        return False

    # comar check..
    comar = os.path.join(dir, "comar")
    if os.path.exists(comar):
        try:
            shutil.copytree(comar, os.path.join(target, "comar"))
        except Exception, e:
            print "Error copying comar files: %s" % e
            return False
    # files/ check
    files = os.path.join(dir, "files")
    if os.path.exists(files):
        try:
            shutil.copytree(files, os.path.join(target, "files"))
        except Exception, e:
            print "Error copying files directory: %s" % e
            return False

    try:
        tgtPath = os.path.join(union_dir(), "root", ".solus", "packager")
        tgtDir = os.path.dirname(tgtPath)
        if not os.path.exists(tgtDir):
            os.makedirs(tgtDir)
        shutil.copyfile(config_path(), tgtPath)
    except Exception, e:
        print "Error copying ypkg config file: %s" % e
        return False

    # component.xml..
    component = os.path.join(dir, "..", "component.xml")
    if os.path.exists(component):
        component = os.path.abspath(component)
        try:
            shutil.copyfile(component, os.path.join(union_dir(), "WORK/component.xml"))
        except Exception, e:
            print "Error copying component.xml: %s" % e
            return False
    return True


def up_root():
    ''' Get the root system up '''
    global update_mode

    # Get the base profile image running read-only.
    root_opts = "ro" if not update_mode else "rw"
    if not do_mount(image_path(), lower_dir(), type="ext4", opts="loop,%s" % root_opts):
        print "Unable to mount image - aborting"
        clean_exit(1)

    # Work from an overlayfs
    if not update_mode:
        if not do_mount("overlay", union_dir(), type="overlay", opts="lowerdir=%s,upperdir=%s,workdir=%s" % (lower_dir(),upper_dir(),work_dir())):
            print "Unable to mount overlay - aborting"
            do_umount(lower_dir())
            clean_exit(1)

    if not do_mount("/dev/", os.path.join(union_dir(), "dev"), bind=True):
        print "vfs failure - aborting"
        down_root()
        clean_exit(1)

    if not os.path.exists(os.path.join(union_dir(), "dev/pts")):
        try:
            os.makedirs(os.path.join(union_dir(), "dev/pts"))
        except Exception, e:
            print "Unable to make /dev/pts dir: %s" % e
            down_root()
            clean_exit(1)

    if not do_mount("devpts", os.path.join(union_dir(), "dev/pts"), type="devpts", opts="gid=5,mode=620"):
        print "vfs failure - aborting"
        down_root()
        clean_exit(1)
    if not do_mount("proc", os.path.join(union_dir(), "proc"), type="proc"):
        print "vfs failure - aborting"
        down_root()
        clean_exit(1)
    if not do_mount("sysfs", os.path.join(union_dir(), "sys"), type="sysfs"):
        print "vfs failure - aborting"
        down_root()
        clean_exit(1)

    # We only want package cache in update mode
    if not update_mode:
        if not os.path.exists(archive_dir()):
            try:
                os.makedirs(archive_dir())
            except Exception, e:
                print "Unable to construct target archive dir %s" % e
                down_root()
                clean_exit(1)
        if not os.path.exists(ccache_dir()):
            try:
                os.makedirs(ccache_dir())
            except Exception, e:
                print "Unable to construct target ccache dir %s" % e
                down_root()
                clean_exit(1)
    if not os.path.exists(package_dir()):
        try:
            os.makedirs(package_dir())
        except Exception, e:
            print "Unable to construct target package dir %s" % e
            down_root()
            clean_exit(1)

    if not update_mode:
        if not do_mount(ARCHIVEDIR, archive_dir(), bind=True):
            print "Archives bind-mount failure"
            down_root()
            clean_exit(1)
        if not do_mount(CCACHE_DIR, ccache_dir(), bind=True):
            print "ccache bind-mount failure"
            down_root()
            clean_exit(1)
    if not do_mount(PACKAGE_DIR, package_dir(), bind=True):
        print "package bind-mount failure"
        down_root()
        clean_exit(1)

    try:
        shutil.copyfile("/etc/resolv.conf", os.path.join(union_dir(), "etc/resolv.conf"))
    except Exception, e:
        print "resolv.conf not copied, connectivity in builder may be broken"
        print e

    if os.path.exists("/etc/eopkg/eopkg.conf"):
        try:
            tgt = os.path.join(union_dir(), "etc/eopkg/eopkg.conf")
            if os.path.exists(tgt):
                os.unlink(tgt)
            shutil.copyfile("/etc/eopkg/eopkg.conf", tgt)
            print "Copied host eopkg.conf"
        except Exception, e:
            print "Unable to copy host eopkg.conf: %s" % e

    if os.path.exists(os.path.join(union_dir(), "var/run/dbus/pid")):
        try:
            os.unlink(os.path.join(union_dir(), "var/run/dbus/pid"))
            print "Removing stale d-bus file"
        except Exception, e:
            print "Unable to remove stale d-bus file"

def down_root():
    ''' Down le roots '''
    global did_mount

    if os.path.exists(os.path.join(union_dir(), "var/run/dbus/pid")):
        with open(os.path.join(union_dir(), "var/run/dbus/pid"), "r") as pid:
            p = pid.read().strip()
            print "Killing d-bus pid: %s" % p
            os.system("kill %s" % p)
            time.sleep(0.5)
            if os.path.exists(os.path.join("/proc", p)):
                print "Force-killing d-bus pid: %s" % p
                os.system("kill -9 %s" % p)
    else:
        print "%s does not exist.. ?" % os.path.join(union_dir(), "var/run/dbus/pid")

    dev = False
    with open("/etc/mtab", "r") as mounts:
        for line in mounts.readlines():
            line = line.replace("\r","").replace("\n","").strip()
            fields = line.split()
            if fields[1].startswith(union_dir()) and fields[1].strip() != union_dir():
                if fields[1].endswith("/dev"):
                    dev = True
                else:
                    print "umounting %s" % fields[1]
                    do_umount(fields[1])
    if dev:
        print "Umounting bind-mount /dev"
        do_umount(os.path.join(union_dir(), "dev"))

    do_umount(union_dir())
    if not update_mode:
        do_umount(lower_dir())
    did_mount = False


if __name__ == "__main__":
    main()
