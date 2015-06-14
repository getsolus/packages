#!/usr/bin/env python

#  pbump.py: Bump pspec.xml
#
#  Copyright 2015 Ikey Doherty <iikey@solus-project.com>
#
#  WARNING: Not well tested, strips comments, and reorders attributes. Crap error handling
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.

import xml.etree.ElementTree as ET
import sys
import os
import xml.dom.minidom as minidom
import datetime
import commands
from configobj import ConfigObj

''' Example config file
~/.solus/packager

[Packager]
Name=Your Name Goes Here
Email=Your Email Goes Here
'''

if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    print "Not enough arguments - aborting"
    #    sys.exit(1)
    homeDir = os.environ ["HOME"]
    config = ".solus/packager"
    config_p = os.path.join(homeDir, config)
    if not os.path.exists(config_p):
        print "Config file not found at %s" % config_p
        sys.exit (1)

    config = ConfigObj(config_p)
    newname = config["Packager"]["Name"]
    newemail = config["Packager"]["Email"]

    if not os.path.exists("pspec.xml"):
        print "pspec.xml doesn\'t exist - aborting"
        sys.exit(1)

    tree = ET.parse("pspec.xml")
    root = tree.getroot()

    hist = root.findall("History")
    last_update = hist[0].findall("Update")[0]
    rel = int(last_update.attrib['release'])
    vers = str(last_update.findall("Version")[0].text)

    # 10-06-2014
    d = datetime.date.today()
    f = d.strftime('%m-%d-%Y')
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
    ent.text = vers
    ent = ET.SubElement(newrel, "Comment")
    ent.tail = "\n            "
    ent.text = "Package bump"
    newrel.attrib['release'] = str(rel)
    ent = ET.SubElement(newrel, "Name")
    ent.tail = "\n            "
    ent.text = newname
    ent = ET.SubElement(newrel, "Email")
    ent.text = newemail
    ent.tail = "\n        "

    s = ET.tostring(root, 'utf-8').replace("\r\n", "\n").replace("\t", "    ")
    complete = "<?xml version=\"1.0\" ?>\n<!DOCTYPE PISI SYSTEM \"https://solus-project.com/standard/pisi-spec.dtd\">\n" + s

    with open ("pspec.xml", "w") as output:
        output.writelines(complete)

    print "Bumped to %s" % rel
