#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  grab-nvr.py - inserted into ISO generation to grab Name-Version-Release files
#
#  Copyright 2015 Ikey Doherty <ikey@solus-project.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#

import subprocess
import os
import pisi.api
import pisi.db.installdb

def main():
    pkgs = pisi.api.list_installed()
    db = pisi.db.installdb.InstallDB()

    with open("packages.nvr", "w") as outp:
        for pkgn in sorted(pkgs):
            pkg = db.get_package(pkgn)
            outp.write("%s\t%s\t%s\n" % (pkgn,pkg.version,pkg.release))
            outp.flush()

def main2():
    pkgs = pisi.api.list_installed()
    ret = dict()
    db = pisi.db.installdb.InstallDB()
    for pkgn in pkgs:
        pkg = db.get_package(pkgn)
        sourcen = pkg.source.name
        if sourcen in ret:
            continue
        ret[sourcen] = "%s\t%s\t%s" % (sourcen, pkg.version, pkg.release)
    with open("sources.nvr", "w") as outp:
        for item in sorted(ret.keys()):
            outp.write(ret[item] + "\n")

if __name__ == "__main__":
    main()
    main2()
