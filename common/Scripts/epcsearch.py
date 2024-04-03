#!/usr/bin/env python3
#
#  epcsearch.py - find pkg-config names
#
#  Copyright 2015 Ikey Doherty <ikey@solus-project.com>
#  Copyright 2024 Solus Developers <releng@getsol.us>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.

import sys

import pisi


def usage(ext=1):
    print("Usage: %s [pkg-config names]" % sys.argv[0])
    sys.exit(ext)


def main():
    if len(sys.argv) < 2:
        usage(0)
    pcs = sys.argv[1:]
    fdb = pisi.db.filesdb.FilesDB()
    pdb = pisi.db.packagedb.PackageDB()

    availPcs, availPcs32 = pdb.get_pkgconfig_providers()

    for pkgconfig in pcs:
        hit = False
        if pkgconfig in availPcs:
            print(f"pkgconfig({pkgconfig}) found in: {availPcs[pkgconfig]}")
            hit = True
        if pkgconfig in availPcs32:
            print(f"pkgconfig32({pkgconfig}) found in: {availPcs32[pkgconfig]}")
            hit = True
        if hit:
            continue
        pc = fdb.get_pkgconfig_provider(pkgconfig)
        if not pc:
            print(f"Error: {pkgconfig} not found in repository or local install")
            continue
        print(f"{pkgconfig} found in: {pc.name}")
        print("Warning: Package does not appear in repository")


if __name__ == "__main__":
    main()
