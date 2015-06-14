#!/usr/bin/env python

#  yconvert.py - convert existing package into YML format
#
#  USAGE: yconvert.py pspec.xml
#  Copyright 2015 Ikey Doherty <iikey@solus-project.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.

import xml.etree.ElementTree as ET
import sys
import os
import xml.dom.minidom as minidom
import commands

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Provide pspec.xml"
        sys.exit(1)
    if not sys.argv[1].endswith("pspec.xml"):
        print "This doesn\'t look like a pspec.xml. Aborting"
        sys.exit(1)
    if not os.path.exists(sys.argv[1]):
        print "pspec.xml doesn\'t exist - aborting"
        sys.exit(1)

    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    archive = root.findall("Source/Archive")[0]

    name = root.findall("Source/Name")[0].text
    homepage = None
    t = root.findall("Source/Homepage")
    if t and len(t) > 0:
        homepage = t[0].text
    lic = root.findall("Source/License")
    licenses = [x.text for x in lic]


    hist = root.findall("History")
    last_update = hist[0].findall("Update")[0]
    rel = int(last_update.attrib['release']) + 1
    version = str(last_update.findall("Version")[0].text)

    description = root.findall("Source/Description")[0].text
    summary = root.findall("Source/Summary")[0].text

    depsi = root.findall("Source/BuildDependencies/Dependency")
    pcdeps = ["pkgconfig(%s)" % (x.text) for x in depsi if "type" in x.attrib and x.attrib['type'] == "pkgconfig"]
    deps = [x.text for x in depsi if "pkgconfig(%s)" % x.text not in pcdeps]

    url = archive.text
    file = url.split("/")[-1]
    r = 0
    try:
        r = os.system("wget \"%s\"" % url)
    except:
        print "Failed to download file"
        sys.exit(1)
    if r != 0:
        print "Failed to download file"
        sys.exit(1)

    sha256 = commands.getoutput("sha256sum %s" % file).split()[0].strip()
    os.unlink(file)

    d = """
name        : %(name)s
version     : %(version)s
release     : %(release)s
source      :
    - %(tarball)s : %(sha256)s
""" % { "name": name, "version": version, "release": rel, "tarball": url, "sha256": sha256}
    if homepage:
        d += "homepage    : %s\n" % homepage
    d += "license     :\n"
    for lic in licenses:
        d += "    - %s\n" % lic
    d += "summary     : %s\n" % summary
    if len(pcdeps) > 0 or len(deps) > 0:
        d += "builddeps   :\n"
        for dep in pcdeps:
            d += "    - %s\n" % dep
        for dep in deps:
            d += "    - %s\n" % dep

    d += "description : |\n"
    for line in description.split("\n"):
        line = line.strip()
        d += "    %s\n" % line
    d += """setup      : |
    %configure
build      : |
    %make
install    : |
    %make_install
"""

    with open ("package.yml", "w") as output:
        output.writelines(d.strip() + "\n")
