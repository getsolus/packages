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

class Pkg:
    """ Simplistic representation of a package """
    
    name = None
    version = None
    release = None
    
    def __init__(self, name, version, release):
        self.name = name
        self.version = version
        self.release = release

class Comparator:
    """ Handle the grunt work of extracting the changes between the ISOs """

    basedir = None
    sources = None

    added = None
    removed = None
    changeTable = None
    mapping = None

    def __init__(self):
        us = os.path.dirname(__file__)
        self.basedir = os.path.abspath(os.path.join(us, "..", ".."))
        self.sources = dict()

        # build a map list for name -> directory for odd things like libX11
        for item in os.listdir(self.basedir):
            self.sources[item.lower()] = os.path.join(self.basedir, item)

        self.mapping = {
            "gd": "libgd",
            "libcairo": "cairo",
            "libgnome-desktop": "gnome-desktop",
            "libgtksourceview": "gtksourceview",
            "modem-manager": "modemmanager",
            "libwebkit-gtk": "webkitgtk3",
        }

    def add_remove(self, l, r):
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

        self.added = [x for x in rp if x not in lp]
        self.removed = [x for x in lp if x not in rp]
        
    def get_source_dir(self, pkgname):
        """ TODO: Handle weird-ass renames """
        pkgname = pkgname.lower()
        if pkgname in self.sources:
            return self.sources[pkgname]
        return os.path.join(basedir, self.sources[self.mapping[pkgname]])

    def get_log(self, opkg, pkg):
        """ Return the log for a given package """
        gitp = self.get_source_dir(pkg.name)
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

    def seed_table(self, p):
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

    def changed(self, l,r):
        lf = os.path.join("./releases", l, "sources.nvr")
        rf = os.path.join("./releases", r, "sources.nvr")
        
        if not os.path.exists(lf) or not os.path.exists(rf):
            print("Missing release")
            sys.exit(1)
        lp = dict()
        rp = dict()

        lp = self.seed_table(lf)
        rp = self.seed_table(rf)

        self.changeTable = dict()

        for key in rp.keys():
            if key not in lp:
                continue
            pkg = rp[key]
            opkg = lp[key]
            if int(pkg.release) != int(opkg.release):
                diff = self.get_log(opkg, pkg)
                self.changeTable[pkg.name] = diff

    def doTheThings(self, v1, v2):
        self.add_remove(v1, v2)
        self.changed(v1, v2)

        with open("changes.md", "w") as changes:
            if len(self.added) > 0:
                changes.write("#### Packages added to this release:\n\n")
                for a in self.added:
                    changes.write(" - %s\n" % a)
                changes.write("\n\n")
            if len(self.removed) > 0:
                changes.write("#### Packages removed from this release:\n\n")
                for a in self.removed:
                    changes.write("- %s\n" % a)
                changes.write("\n\n")
            if len(self.changeTable) > 0:
                changes.write("#### Changes in this release:\n\n")
                for key in self.changeTable.keys():
                    changes.write("**%s**\n\n" % key)
                    if key not in self.changeTable or self.changeTable[key] is None:
                        print("%s MISSING !!! " % key)
                    for line in self.changeTable[key]:
                        spl = line.split("|")
                        com = spl[0]
                        words = "|".join(spl[1:])
                        href = "https://dev.getsol.us/source/%s/browse/master/;%s" % (key, com)
                        changes.write(" - [%s](%s)\n" % (words, href))
                    changes.write("\n\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Invalid usage: %s [version1] [version2]" % sys.argv[0])
        sys.exit(1)
    comp = Comparator()
    comp.doTheThings(sys.argv[1], sys.argv[2])   
