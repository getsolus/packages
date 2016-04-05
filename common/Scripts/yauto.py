#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  yauto.py
#  
#  Copyright 2013 Ikey Doherty <ikey@solusos.com>
#  Copyright 2015 Ikey Doherty <iikey@solus-project.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
import os
import sys
import os.path
import dloader
import datetime
import shutil

from configobj import ConfigObj

''' Example config file
~/.evolveos/packager

[Packager]
Name=Your Name Goes Here
Email=Your Email Goes Here
'''

# What we term as needed doc files
KnownDocFiles = [ "COPYING", "COPYING.LESSER", "ChangeLog", "COPYING.GPL", "AUTHORS", "BUGS", "CHANGELOG", "LICENSE"]

# Compile type to build 'actions.py'
GNOMEY = 1
AUTOTOOLS = 2
CMAKE = 3
PYTHON_MODULES = 4
PERL_MODULES = 5

class DepObject:

    name = None
    version = None

class AutoPackage:

    package_prefix = ""

    buildpl = False
    makefile = False

    def __init__(self, uri):
        self.package_uri = uri
        homeDir = os.environ ["HOME"]
        config = ".solus/packager"
        self.config_dir = os.path.join (homeDir, config)
        if not os.path.exists (self.config_dir):
            print "Config file not found at %s" % self.config_dir
            sys.exit (-1)

        # See the above commentary for details on the file format
        self.config = ConfigObj (self.config_dir)
        self.email = self.config["Packager"]["Email"]
        self.packager_name = self.config["Packager"]["Name"]

        # Templates
        us = os.path.dirname(os.path.abspath(__file__))
        base_dir = "/".join (us.split ("/")[:-1])
        self.template_dir = os.path.join (base_dir, "Templates")

        self.build_deps = list()

        self.doc_files = list()

    def verify (self):
        print "Verifying %s" % self.package_uri
        self.file_name = self.package_uri.split ("/")[-1]
        self.file_name_full = os.path.abspath (self.file_name)
        print self.file_name
        try:
            dloader.download_file (self.package_uri)
            self.sha256sum = dloader.get_sha256sum(self.file_name)
        except Exception, e:
            print e
            return False
        return True

    def examine_source (self):
        splits = self.file_name.split (".")
        suffix = "".join(splits [-2:]).replace ("bzip2", "bz2")
        # Find out pspec file type
        if suffix.endswith ("zip"):
            suffix = "zip"
        self.file_type = suffix

        # Work out the version number
        path,ext = os.path.splitext (self.file_name)
        version = path.split ("-")[-1].split(".")[:-1]
        version_string = ".".join(version)
        self.version_string = version_string

        # Package name, including hyphens
        self.package_name = "-".join(path.split("-")[:-1])
        self.compile_type = None

        print "Package: %s\nVersion: %s" % (self.package_name, self.version_string)

        # Set up temporary
        self.temp_dir = os.path.abspath ("./TEMP")
        os.mkdir (self.temp_dir)
        self.current_dir = os.getcwd ()

        os.chdir (self.temp_dir)
        os.system ("tar xf \"%s\"" % self.file_name_full)

        known_types = list()

        # Check for certain files..
        for root,dirs,files in os.walk (os.getcwd ()):
            depth = root[len(path) + len(os.path.sep):].count(os.path.sep)
            if depth == 3:
                print "bailing"
                # We're currently two directories in, so all subdirs have depth 3
                dirs[:] = [] # Don't recurse any deeper
            for file in files:
                if file in KnownDocFiles:
                    # Append files for pisitools.dodoc ()
                    if file not in self.doc_files:
                        self.doc_files.append (file)
                        print "Added %s" % file
                if file == "Makefile":
                    self.makefile = True
                if "configure.ac" in file:
                    # Examine this fella for build deps
                    self.build_deps = self.check_build_deps(os.path.join(root, file))
                if "configure" in file:
                    # Check if we need to employ certain hacks needed in gnome packages
                    fPath = os.path.join (root, file)
                    print "Checking %s for use of g-ir-scanner" % fPath

                    if self.check_is_gnomey (fPath):
                        known_types.append(GNOMEY)
                    else:
                        known_types.append(AUTOTOOLS)
                if "CMakeLists.txt" in file:
                    # This will use the actions with cmake
                    known_types.append(CMAKE)
                if "setup.py" in file:
                    # this is a python module.
                    known_types.append(PYTHON_MODULES)
                if "Makefile.PL" in file or "Build.PL" in file:
                    # This is a perl module
                    known_types.append(PERL_MODULES)
                if "BUILD.PL" in file:
                    self.buildpl = True

        # We may have hit several systems..
        if CMAKE in known_types:
            print "cmake"
            self.compile_type = CMAKE
        elif GNOMEY in known_types:
            print "gnomey"
            self.compile_type = GNOMEY
        elif AUTOTOOLS in known_types:
            print "autotools"
            self.compile_type = AUTOTOOLS
        elif PYTHON_MODULES in known_types:
            print "python"
            self.compile_type = PYTHON_MODULES
        elif PERL_MODULES in known_types:
            print "perl"
            self.compile_type = PERL_MODULES
        else:
            print "unknown"

        # Clean up on aisle 3
        os.chdir (self.current_dir)
        shutil.rmtree (self.temp_dir)

        # Always delete
        if os.path.exists (self.file_name):
            os.remove (self.file_name)

    def check_build_deps(self, path):
        deps = list()
        with open(path, "r") as read:
            for line in read.readlines():
                line = line.replace("\n","").replace("\r","").strip()
                # Currently only handles configure.ac
                if "PKG_CHECK_MODULES" in line:
                    splits = line.split(",")
                    part = splits[1] if len(splits) > 1 else splits[0]
                    part = part.replace("[","").replace(")","").replace("]","")
                    splits = part.split(">=")
                    pkg = splits[0].strip()
                    dep = DepObject()
                    dep.name = pkg
                    if len(splits) > 1:
                        version = splits[1].strip()
                        # Can happen, we don't handle variable expansion.
                        if "$" in version:
                            continue
                        dep.version = version
                    # Check it hasn't been added
                    objs = [x for x in deps if x.name == dep.name]
                    if len(objs) == 0:
                        deps.append(dep)

        return deps

    def create_yaml(self):
        ''' Attempt creation of a package.yaml... '''
        with open('package.yml', 'w') as yml:
            mapping = { "NAME" : self.package_name,
                        "VERSION" : self.version_string,
                        "SOURCE": self.package_uri,
                        "SHA256SUM": self.sha256sum }
            
            tmp = """name       : %(NAME)s
version    : %(VERSION)s
release    : 1
source     :
    - %(SOURCE)s : %(SHA256SUM)s
license    : GPL-2.0 # CHECK ME
summary    : PLEASE FILL ME IN
component  : PLEASE FILL ME IN

description: |
    PLEASE FILL ME IN""" % mapping

            totalStr = tmp
            setup = None
            build = None
            install = None

            totalStr += "\nbuilddeps  :\n"
            if self.build_deps is not None and len(self.build_deps) > 0:
                for dep in self.build_deps:
                    if len(dep.name.strip()) == 0:
                        continue
                    totalStr += "    - pkgconfig(%s)\n" % dep.name
            if self.compile_type == GNOMEY:
                setup = "%configure --disable-static"
            elif self.compile_type == CMAKE:
                setup = "%cmake ."
            elif self.compile_type == PYTHON_MODULES:
                setup = "python setup.py configure"
                build = "python setup.py build"
                install = "python setup.py install --root=%installroot% --no-compile -O0"
            elif self.compile_type == PERL_MODULES:
                if self.buildpl:
                    setup = "perl Build.PL installdirs=vendor destdir=%installroot%"
                else:
                    setup = "perl Makefile.PL PREFIX=/usr INSTALLDIRS=vendor DESTDIR=%installroot%"
                if not self.makefile:
                    build = "perl Build"
                    install = "perl Build install"
                sample_actions = os.path.join (self.template_dir, "actions.perlmodules.sample.py")

            if setup is None:
                setup = "%configure"
            if build is None:
                build = "%make"
            if install is None:
                install = "%make_install"

            mapping = { "SETUP": setup, "BUILD" : build, "INSTALL" : install }
            tmpl = """setup      : |
    %(SETUP)s
build      : |
    %(BUILD)s
install    : |
    %(INSTALL)s
""" % mapping
            totalStr += "\n" + tmpl

            yml.writelines(totalStr.replace("\n\n", "\n"))
            yml.flush()

    def check_is_gnomey (self, path):
        with open (path, "r") as makefile:
            lines = makefile.read ()
            if "g-ir-scanner" in lines or "g_ir_scanner" in lines:
                return True
        return False

if __name__ == "__main__":
    if len (sys.argv) < 2:
        print "%s: <URI>" % sys.argv[0]
        sys.exit (-1)

    p  = AutoPackage (sys.argv[1])
    if not p.verify ():
        print "Unable to locate given URI"
    else:
        print "Completed verification"
        p.examine_source ()
        p.create_yaml ()
