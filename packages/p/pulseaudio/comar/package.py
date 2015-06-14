#!/usr/bin/python
import os

OUR_ID = 58
OUR_NAME = "pulse"
OUR_DESC = "PulseAudio"

ACCESS_ID = 59
ACCESS_NAME = "pulse-access"


def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    try:
        os.system("groupadd -g %d %s" % (OUR_ID, OUR_NAME))
        os.system("groupadd -g %d %s" % (ACCESS_ID, ACCESS_NAME))
        os.system("useradd -m -d /var/run/pulse -r -s /bin/false \
            -u %d -g %d %s -c %s" % (OUR_ID, OUR_ID, OUR_NAME, OUR_DESC))
    except:
        pass


def postRemove():
    try:
        os.system("userdel %s" % OUR_NAME)
        os.system("groupdel %s" % OUR_NAME)
        os.system("groupdel %s" % ACCESS_NAME)
    except:
        pass
