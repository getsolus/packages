#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  license_scan.py
#  
#  Copyright 2015 Ikey Doherty <iikey@solus-project.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
import os
import sys
import os.path
import hashlib

licenses = dict()

def gen_list():
    global licenses

    for i in ["../licenses.spdx", "../licenses.extra"]:
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), i)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r") as lics:
            for i in lics.readlines():
                i = i.strip().replace("\n","").replace("\r","")
                if i == "":
                    continue
                spl = i.split()
                licenses[spl[0].strip()] = spl[1].strip()

gen_list()

found_licenses = list()
bad_licenses = dict()

matches = {
    "GNU LIBRARY GENERAL PUBLIC LICENSE": "LGPL-2.0",
    "Version 2, June 1991" : "GPL-2.0",
    "MIT License": "MIT",
    "Version 2.1, February 1999": "LGPL-2.1",
    "Version 2.0, January 2004": "Apache-2.0",
    "GNU LESSER GENERAL PUBLIC LICENSE" : "LGPL-3.0",
    "Version 3, 29 June 2007": "GPL-3.0",
    "SGI FREE SOFTWARE LICENSE B": "SGI-B-2.0",
    "SIL OPEN FONT LICENSE Version 1.1": "OFL-1.1",
    "Version 1.1, March 2000": "GFDL-1.1",
    "THIS WORK IS IN PUBLIC DOMAIN:": "Public-Domain",
    "are placed into the public domain": "Public-Domain",
    "This code is released under the libpng license": "Libpng",
    "Version: MPL 1.1": "MPL-1.1",
    "Apache License, Version 2.0 ": "Apache-2.0",
    "http://mozilla.org/MPL/2.0/": "MPL-2.0",
    "3-clause": "BSD-3-Clause",
    "GPL 2.0/LGPL 2.1/MPL 1.1": "LGPL-2.1",
}

def add_license(l, fname=None):
    global found_licenses

    if l in found_licenses:
        return
    found_licenses.append(l)
    return

def scan_file(p):
    with open(p, "r") as inf:
        for line in inf.readlines():
            line = line.replace("\n","").replace("\r","").strip()
            if line == "":
                continue
            for k in matches:
                if k in line:
                    add_license(matches[k], p)
                    return True
    return False


def scan_tree(p):
    global licenses
    global bad_licenses
    global found_licenses

    for root,dirs,files in os.walk(p):
        potentials = [x for x in files if x.lower().startswith("license") or x.lower().startswith("licence") or x.lower().startswith("copying")]
        if len(potentials) == 0:
            continue
        for p in potentials:
            # Testing purposes..
            if os.path.abspath(os.path.join(root,p)) == os.path.abspath(__file__):
                continue
            # obtain hash
            try:
                fname = os.path.join(root,p)
                f = open(fname)
                txt = f.read()
                f.close()
                h = hashlib.sha1(txt).hexdigest()
                if h in licenses:
                    add_license(licenses[h], fname)
                else:
                    if not scan_file(fname):
                        # These are currently the only ones we want debugs for.
                        if p.startswith("COPYING") or p.startswith("LICENSE") or p.startswith("LICENCE"):
                            if h not in bad_licenses:
                                bad_licenses[h] = list()
                            bad_licenses[h].append(fname)
            finally:
                f.close()
    return found_licenses

if __name__ == "__main__":
    lic = scan_tree(".")

    for h in bad_licenses:
        print("Unknown hash: %s %s" % (bad_licenses[h][0], h))

    print("Licenses: %s" % ", ".join(lic))
