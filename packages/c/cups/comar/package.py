#!/usr/bin/python

import os, re
import commands

ID = 19
NAME = "lpadmin"


OUR_ID = 9
OUR_NAME = "lp"
OUR_DESC = "Print Service User"


def is_group_empty(group):
    out = commands.getoutput("groupmems -l -g %s" % group)
    if len(out.strip()) == 0:
        return True
    return False

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    try:
        os.system("groupadd -g %d %s" % (ID, NAME))
    except:
        pass
    try:
        os.system ("groupadd -g %d %s" % (OUR_ID, OUR_NAME))
        os.system ("useradd -m -d /var/spool/cups -r -s /bin/false -u %d -g %d %s -c \"%s\"" % (OUR_ID, OUR_ID, OUR_NAME, OUR_DESC))
        if os.path.exists("/var/spool/cups"):
            os.system("chown -R %s:%s /var/spool/cups" % (ID, ID))
    except:
        pass

def postRemove():
    empty = is_group_empty("lpadmin")

    if (empty):
        try:
            os.system("groupdel %s" % NAME)
        except:
            pass
    try:
        os.system ("userdel %s" % OUR_NAME)
        os.system ("groupdel %s" % OUR_NAME)
    except:
        pass
