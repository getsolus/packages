#!/usr/bin/env python
import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
	# As soon as we install let's update the font cache
	os.system ("fc-cache -fv")
