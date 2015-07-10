#!/usr/bin/python

import os, re
import commands

OUR_ID = 19
OUR_NAME = "lpadmin"


def is_group_empty(group):
    out = commands.getoutput("groupmems -l -g %s" % group)
    if len(out.strip()) == 0:
        return True
    return False

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    try:
        os.system("groupadd -g %d %s" % (OUR_ID, OUR_NAME))
    except:
        pass

def postRemove():
    empty = is_group_empty("lpadmin")

    if (empty):
        try:
            os.system("groupdel %s" % OUR_NAME)
        except:
            pass
