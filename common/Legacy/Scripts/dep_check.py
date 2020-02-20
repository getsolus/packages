#!/usr/bin/env python

import pisi.api
import commands
import sys
import os

blacklist = ('/lib/linux-gate.','/lib/libm.', '/lib/ld-linux.', '/lib/libc.', '/lib/librt.', 'linux-gate.so.1', '/lib/libpthread.', '/lib/libdl.')

def package_for_file (filename):
	return pisi.api.search_file (filename)
	
def blacklisted (filename):
	if not filename.startswith("/"):
		filename = "/%s" % filename	
	for f in blacklist:
		if f in filename:
			return True
	return False
		
def ldd (filename):
	
	if "usr/share" in filename:
		return

	ldd = commands.getoutput ("ldd %s" % filename)
	
	for line in ldd.split ("\n"):
		line = line.replace("\n","").replace("\r","").strip()
		if line == "":
			continue
		splits = line.split ("=>")
		sourceLib = splits[0].strip()
		if len(splits) > 1:
			sourceLib = splits[1].strip().split (" ")[0]
		else:
			sourceLib = sourceLib.split (" ")[0].strip()
			
		# Skip blacklisted
		if blacklisted (sourceLib):
			continue
			
		if os.path.exists (sourceLib):	
			dep = package_for_file (sourceLib)
			
			if len(dep) > 0:
				# Circular dependencies are ugly :p
				if dep[0][0] == sys.argv[1]:
					break
				# Check its not accounted for
				if not dep[0][0] in dependsOn:
					dependsOn[ dep[0][0] ] = "/%s" % dep [0][1][0]




if __name__ == "__main__":

	if len(sys.argv) != 2:
		print "Usage: %s package_name" % sys.argv[0]
		sys.exit (1)
	
	pkg = sys.argv[1]
	try:
		meta,files,other = pisi.api.info_name (pkg, True)
	except:
		print "Could not find package: %s" % pkg
		sys.exit (1)
		
	dependsOn = dict()
			
	for file in files.list:
		filename = file.path
		if not filename.startswith("/"):
			filename = "/%s" % filename
			

		if hasattr(file, 'type'):
			if file.type == "executable":
				ldd (filename)
			elif file.type == "library" and ".so" in filename:
				ldd (filename)
		else:
			if ".so" in filename:
				ldd (filename)


	print "[ Dependencies ]"
	for dep in dependsOn:
		print "Depends on %s from %s" % (dependsOn[dep], dep)

	print "\n[ XML Dependencies ]"
	print "<RuntimeDependencies>"
	for dep in dependsOn:
		print "    <Dependency>%s</Dependency>" % dep
	print "</RuntimeDependencies>"
	
	# Suggest build dependencies
	print "\n[XML Build Dependencies]"
	print "<BuildDependencies>"
	for dep in dependsOn:
		package = "%s-devel" % dep
		try:
			subject = pisi.api.info_name (package, True)
			print "    <Dependency>%s</Dependency>" % package
		except:
			print "    <!-- Info: no %s package - consider splitting -->" % package
	print "</BuildDependencies>"
