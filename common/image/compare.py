#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  compare.py - compare NVR differences between 2 releases
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
import commands

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def add_remove(l,r):
    lf = os.path.join("./releases", l, "packages.nvr")
    rf = os.path.join("./releases", r, "packages.nvr")
    
    if not os.path.exists(lf) or not os.path.exists(rf):
        print("Missing release")
        sys.exit(1)
    lp = list()
    rp = list()
    with open(lf, "r") as inp:
        lp = [x.strip().replace("\n","").replace("\r","").split("\t")[0] for x in inp.readlines() if x != ""]
    with open(rf, "r") as inp:
        rp = [x.strip().replace("\n","").replace("\r","").split("\t")[0] for x in inp.readlines() if x != ""]

    added = [x for x in rp if x not in lp]
    removed = [x for x in lp if x not in rp]
    
    return (added,removed)

class Pkg:
    
    name = None
    version = None
    release = None
    
    def __init__(self, name, version, release):
        self.name = name
        self.version = version
        self.release = release

def get_log(opkg, pkg):
    gitp = os.path.join(basedir, pkg.name)
    if not os.path.exists(gitp + "/.git"):
        print("%s does not exist" % pkg.name)
        return None

    tag = "%s-%s-%s" % (pkg.name,pkg.version,pkg.release)
    otag = "%s-%s-%s" % (opkg.name,opkg.version,opkg.release)
    try:
        res = os.system("git -C \"%s\" rev-list %s >/dev/null 2>/dev/null" % (gitp, otag))
        if res != 0:
            otag = "%s~1" % tag
    except Exception, ex:
        otag = "%s~1" % tag
    try:
        tg = commands.getoutput("git -C \"%s\" describe --tags" % gitp)
        if tg != tag:
            res = os.system("git -C \"%s\" fetch origin" % gitp)
            if res != 0:
                print("Failed to fetch origin for %s" % pkg.name)
        cmd = "git -C \"%s\" --no-pager log --pretty=format:\"%%h|%%an: %%s\" " % (gitp)
        if otag != "%s~1" % tag:
            cmd += "%s..%s" % (otag, tag)
        else:
            cmd += tag
        print cmd
        log = commands.getoutput(cmd)
        spl = log.split("\n")
        if otag == "%s~1" % tag and len(spl) > 1:
            log = "\n".join(spl[:-1])
    except Exception, ex:
        print("Exception: %s" % ex)
        return None
    return log.split("\n")

def changed(l,r):
    lf = os.path.join("./releases", l, "sources.nvr")
    rf = os.path.join("./releases", r, "sources.nvr")
    
    if not os.path.exists(lf) or not os.path.exists(rf):
        print("Missing release")
        sys.exit(1)
    lp = dict()
    rp = dict()

    def seed_table(p):
        ret = dict()
        with open(p, "r") as inp:
            for line in inp.readlines():
                line = line.strip().replace("\r","").replace("\n","")
                if "\t" not in line:
                    continue
                spl = line.split("\t")
                pkg = Pkg(spl[0], spl[1], spl[2])
                ret[spl[0]] = pkg
        return ret
    lp = seed_table(lf)
    rp = seed_table(rf)

    changeTable = dict()

    for key in rp.keys():
        if key not in lp:
            continue
        pkg = rp[key]
        opkg = lp[key]
        if int(pkg.release) != int(opkg.release):
            diff = get_log(opkg, pkg)
            changeTable[pkg.name] = diff
    
    return changeTable

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Invalid usage: %s [version1] [version2]" % sys.argv[0])
        sys.exit(1)
    (added,removed) = add_remove(sys.argv[1], sys.argv[2])
    changeTable = changed(sys.argv[1], sys.argv[2])
    
    with open("changes.htm", "w") as changes:
        changes.write("<html><head><title>Changelog</title><body>\n")
        if len(added) > 0:
            changes.write("<h4>Packages added to this release:</h4>\n<ul>\n")
            for a in added:
                changes.write("<li>%s</li>\n" % a)
            changes.write("\n</ul>\n")
        if len(removed) > 0:
            changes.write("<h4>Packages removed from this release:</h4>\n<ul>\n")
            for a in removed:
                changes.write("<li>%s</li>\n" % a)
            changes.write("\n</ul>\n")
        if len(changeTable) > 0:
            changes.write("<h4>Changes in this release:</h4>\n\n")
            for key in changeTable.keys():
                changes.write("<b>%s</b>\n<ul>\n" % key)
                for line in changeTable[key]:
                    spl = line.split("|")
                    com = spl[0]
                    words = "|".join(spl[1:])
                    href = "https://git.solus-project.com/packages/%s/commit/?id=%s" % (key, com)
                    changes.write("<li><a href=\"%s\">%s</a></li>" % (href, words))
                changes.write("\n</ul>\n")
                changes.write("\n")
        changes.write("</body></html>")
