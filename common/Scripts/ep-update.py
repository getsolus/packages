#!/usr/bin/env python3

#  ep-update.py: Update a package using a tarball
#
#  USAGE: ep-update.py VERSION UPSTREAM_URL
#  Copyright 2015 Ikey Doherty <iikey@solus-project.com>
#  Copyright 2024 Solus Developers <releng@getsol.us>
#
#  WARNING: Not well tested, strips comments, and reorders attributes. Crap error handling
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.

import configparser
import datetime
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

""" Example config file
~/.config/solus/packager

[Packager]
Name=Your Name Goes Here
Email=Your Email Goes Here
"""

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #    print "Not enough arguments - aborting"
    #    sys.exit(1)
    homeDir = os.environ["HOME"]
    config = ".config/solus/packager"
    config_old = ".solus/packager"
    config_p = os.path.join(homeDir, config)
    config_old_p = os.path.join(homeDir, config_old)

    use_conf = None

    if os.path.exists(config_p):  # New packager exists
        use_conf = config_p
    else:
        if os.path.exists(config_old_p):  # Old only exists
            use_conf = config_old_p
        else:
            print("Config file could not be found.")
            sys.exit(1)

    c = configparser.ConfigParser()
    c.read(use_conf)
    newname = c.get("Packager", "Name")
    newemail = c.get("Packager", "Email")

    if not os.path.exists("pspec.xml"):
        print("pspec.xml doesn't exist - aborting")
        sys.exit(1)

    url = sys.argv[2]
    file = url.split("/")[-1]
    newversion = sys.argv[1]
    r = 0
    try:
        r = os.system(f'wget "{url}"')
    except Exception:
        print("Failed to download file")
        sys.exit(1)
    if r != 0:
        print("Failed to download file")
        sys.exit(1)

    sha1 = subprocess.getoutput(f"sha1sum {file}").split()[0].strip()

    mapping = {
        "tar.bz2": "tarbz2",
        "tbz2": "tarbz",
        "tar.xz": "tarxz",
        "txz": "tarxz",
        "tar.gz": "targz",
        "tgz": "targz",
        "zip": "zip",
    }
    extype = ".".join(url.split(".")[-2:])
    if extype in mapping:
        extension = mapping[extype]
    elif extype.endswith("tar"):
        extension = "tar"
    else:
        extension = "binary"

    tree = ET.parse("pspec.xml")
    root = tree.getroot()

    archive = root.findall("Source/Archive")[0]
    archive.attrib["sha1sum"] = sha1
    archive.attrib["type"] = extension
    archive.text = url

    hist = root.findall("History")
    last_update = hist[0].findall("Update")[0]
    rel = int(last_update.attrib["release"])

    # 10-06-2014
    d = datetime.date.today()
    f = d.strftime("%m-%d-%Y")
    # normal shmaz.
    rel += 1
    newrel = ET.Element("Update")
    newrel.tail = "\n\n        "
    newrel.text = "\n            "
    hist[0].insert(0, newrel)
    ent = ET.SubElement(newrel, "Date")
    ent.tail = "\n            "
    ent.text = f
    ent = ET.SubElement(newrel, "Version")
    ent.tail = "\n            "
    ent.text = newversion
    ent = ET.SubElement(newrel, "Comment")
    ent.tail = "\n            "
    ent.text = f"Update to {newversion}"
    newrel.attrib["release"] = str(rel)
    ent = ET.SubElement(newrel, "Name")
    ent.tail = "\n            "
    ent.text = newname
    ent = ET.SubElement(newrel, "Email")
    ent.text = newemail
    ent.tail = "\n        "

    s = ET.tostring(root, "unicode").replace("\r\n", "\n").replace("\t", "    ")
    complete = (
        '<?xml version="1.0" ?>\n<!DOCTYPE PISI SYSTEM "https://getsol.us/standard/pisi-spec.dtd">\n'
        + s
    )

    os.unlink(file)
    with open("pspec.xml", "w") as output:
        output.writelines(complete)

    print("Now please build to verify your changes")
