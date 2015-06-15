#!/usr/bin/env python

#
#  USAGE: buildwrap.py start|stop|restart
#
#  This requires the following sudo rule (change "ikey" for your username)
#       Cmnd_Alias BOT_CMDS = /usr/bin/evobuild
#       ikey ALL=(ALL) NOPASSWD: BOT_CMDS
#
#  Copyright 2015 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
import os
import commands
import sys
from daemon import runner
import time
import shutil
import subprocess
import shlex
import glob

WorkDir = "/BUILDDIR"
SSH_HOST = "solus-project.com"
BASE_REPO = "https://git.solus-project.com/packages"


def check_output(cmd):
    return subprocess.check_output(shlex.split(cmd))

class Builder():

    def __init__(self):
        self.pidfile_path =  '%s/build.pid' % WorkDir
        self.pidfile_timeout = 5
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'

        self.wd = os.getcwd()

    def report_status(self, id, status):
        try:
            os.system("ssh build@%s status %s %s" % (SSH_HOST, id, status))
        except Exception, e:
            print e
            sys.exit(-1)

    def run(self):
        while True:
            # attempt to get a job. :P
            os.chdir(self.wd)
            output = None
            try:
                output = check_output("ssh build@%s get" % SSH_HOST)
            except Exception, e:
                time.sleep(10)
                continue
            if "\t" not in output:
                time.sleep(10)
                continue

            splits = output.split("\t")
            id = splits[0].replace("\n","")
            pkg = splits[1].replace("\n","")
            tag = splits[2].replace("\n","")
            print "Taking: %s %s" % (pkg, tag)

            clone_uri = "%s/%s" % (BASE_REPO, pkg)

            clone_dir = os.path.join(WorkDir, "CLONE", pkg)
            clone_base = os.path.join(WorkDir, "CLONE")
            if os.path.exists(clone_dir):
                try:
                    shutil.rmtree(clone_dir)
                except Exception, e:
                    self.report_status(id, "FAILED")
                    time.sleep(10)
                    continue

            try:
                if not os.path.exists(clone_base):
                    os.makedirs(clone_base)
            except Exception, e:
                print e
                self.report_status(id, "FAILED")
                time.sleep(10)
                continue

            wd = os.getcwd()
            try:
                os.chdir(clone_base)
                check_output("git clone %s" % clone_uri)
            except Exception, e:
                print e
                self.report_status(id, "FAILED")
                time.sleep(10)
                continue

            try:
                os.chdir(clone_dir)
                check_output("git checkout %s" % tag)
            except Exception, e:
                print e
                self.report_status(id, "FAILED")
                time.sleep(10)
                continue

            yml = os.path.abspath(os.path.join(clone_dir, "package.yml"))
            spec = os.path.abspath(os.path.join(clone_dir, "pspec.xml"))
            tgt = None
            if os.path.exists(yml):
                tgt = yml
            elif os.path.exists(spec):
                tgt = spec
            else:
                print("Cannot determine package type")
                self.report_status(id, "FAILED")
                time.sleep(10)
                continue

            builddir = os.path.join(WorkDir, "BUILD")
            if os.path.exists(builddir):
                try:
                    shutil.rmtree(builddir)
                except Exception, e:
                    print("Cannot remove tree")
                    self.report_status(id, "FAILED")
                    time.sleep(10)
                    continue

            try:
                os.makedirs(builddir)
            except Exception, e:
                print("Cannot create tree")
                self.report_status(id, "FAILED")
                time.sleep(10)
                continue

            os.chdir(builddir)
            cmd = "sudo evobuild build %s -p unstable-x86_64 > \"%s.log\" 2>&1" % (tgt, tag)
            self.report_status(id, "BUILDING")
            try:
                os.system(cmd)
            except Exception, e:
                print e
                self.report_status(id, "FAILED")
                time.sleep(10)
                continue

            pkgs = None
            try:
                f = glob.glob("*.eopkg")
                pkgs = [os.path.basename(x) for x in f]
            except Exception, e:
                print e
                self.report_status(id, "FAILED")
                time.sleep(10)
                continue
            try:
                check_output("scp %s packages@%s:base/incoming/unstable" % (" ".join(pkgs), SSH_HOST))
            except Exception, e:
                print e
                self.report_status(id, "FAILED")
                time.sleep(10)
                continue

            try:
                check_output("scp \"%s.log\" logs@%s:logs/." % (tag, SSH_HOST))
            except Exception, e:
                print e
                self.report_status(id, "FAILED")
                time.sleep(10)
                continue

            # technically finished?
            self.report_status(id, "OK")
            time.sleep(10)

if __name__ == "__main__":
    app = Builder()
    run = runner.DaemonRunner(app)
    run.do_action()
