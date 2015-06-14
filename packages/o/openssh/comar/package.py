#!/usr/bin/python

import os, re
import os.path

OUR_ID = 50
OUR_NAME = "sshd"
OUR_DESC = "SSH Daemon"
OUR_HOME = "/var/lib/sshd/"

HOST_KEY = "/etc/ssh/ssh_host_rsa_key"

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    try:
        os.system ("groupadd -g %d %s" % (OUR_ID, OUR_NAME))
        os.system ("useradd -d %s -r -s /bin/false -u %d -g %d %s -c \"%s\"" % (OUR_HOME, OUR_ID, OUR_ID, OUR_NAME, OUR_DESC))
    except:
        pass

    if not os.path.exists (HOST_KEY):
        os.system ("/usr/bin/ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key")


def postRemove():
    try:
        os.system ("userdel %s" % OUR_NAME)
        os.system ("groupdel %s" % OUR_NAME)
    except:
        pass
