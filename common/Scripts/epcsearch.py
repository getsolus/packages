#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  epcsearch.py - find pkg-config names
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
import pisi

def usage(ext=1):
    print "Usage: %s [pkg-config names]" % sys.argv[0]
    sys.exit(ext)

def main():
    if len(sys.argv) < 2:
        usage(0)
    pcs = sys.argv[1:]
    idb = pisi.db.installdb.InstallDB()
    pdb = pisi.db.packagedb.PackageDB()

    for pkgconfig in pcs:
        pc = pdb.get_package_by_pkgconfig(pkgconfig)
        if not pc:
            pc = idb.get_package_by_pkgconfig(pkgconfig)
            if pc:
                print "%s found in: %s" % (pkgconfig, pc.name)
                print "Warning: Package does not appear in repository"
            else:
                print "Error: %s not found in repository or local install" % pkgconfig
        else:
            print "%s found in: %s" % (pkgconfig, pc.name)

if __name__ == "__main__":
    main()
