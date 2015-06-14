#!/usr/bin/python

import piksemel
import os

def updateGConf (filepath, remove=False):
    parse = piksemel.parse (filepath)
    schemaList = list()

    for xmlfile in parse.tags ("File"):
        path = xmlfile.getTagData ("Path")

        # Only interested in /etc/gconf/schemas
        if "etc/gconf/schemas" in path:
            schemaList.append ("/%s" % path)

    if len(schemaList) > 0:
        os.environ['GCONF_CONFIG_SOURCE'] = 'xml:merged:/etc/gconf/gconf.xml.defaults'
        operation = "--makefile-uninstall-rule" if remove else "--makefile-install-rule"
        cmd = "/usr/bin/gconftool-2 %s %s" % (operation, " ".join(schemaList))
        os.system (cmd)

def setupPackage (metapath, filepath):
    updateGConf (filepath)

def postCleanupPackage (metapath, filepath):
    updateGConf (filepath)
