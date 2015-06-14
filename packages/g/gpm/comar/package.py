import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):

	os.system('install-info --dir-file=/usr/info/dir --info-file=/usr/share/info/gpm.info')
