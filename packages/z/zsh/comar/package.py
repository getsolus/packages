#!/usr/bin/python

import os, re

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
	with open("/etc/shells", "a") as shells:
		shells.write("/bin/zsh\n")

def postRemove():
	s = open("/etc/shells", "r")
	lines = s.readlines()
	s.close()
	s = open("/etc/shells", "w")
	for line in lines:
		if line != "/bin/zsh"+"\n":
			s.write(line)
	s.close()
