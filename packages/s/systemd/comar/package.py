#!/usr/bin/env python
import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    os.system("/usr/bin/systemd-sysusers")
    os.system("/usr/bin/systemd-tmpfiles --create")
