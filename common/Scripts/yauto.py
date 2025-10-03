#!/usr/bin/env python3

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
import mimetypes
import shutil
from release_monitoring import get_release_monitoring

# What we term as needed doc files
KnownDocFiles = [
    "COPYING",
    "COPYING.LESSER",
    "ChangeLog",
    "COPYING.GPL",
    "AUTHORS",
    "BUGS",
    "CHANGELOG",
    "LICENSE",
]

# Compile type to build 'actions.py'
GNOMEY = 1
AUTOTOOLS = 2
CMAKE = 3
PYTHON_MODULES = 4
PERL_MODULES = 5
CABAL = 6
RUBY = 7
RUBY_GEMS = 8
MESON = 9
YARN = 10
WAF = 11
QMAKE = 12
PEP517 = 13
PYTHON_SETUPTOOLS = 14


class DepObject:
    name = None
    version = None


class AutoPackage:
    package_prefix: str = ""

    buildpl: bool = False
    makefile: bool = False

    def __init__(self, uri: str, fallback_package_name: str = None):
        self.package_uri: str = uri

        self.current_dir = None
        self.temp_dir = None
        self.file_name = None
        self.file_name_full = None
        self.file_type = None

        self.sha256sum = None

        self.compile_type = None
        self.component = None
        self.networking = False
        self.package_name = fallback_package_name.lower() if fallback_package_name else None
        self.version_string = None

        # Templates
        us = os.path.dirname(os.path.abspath(__file__))
        base_dir = "/".join(us.split("/")[:-1])
        self.template_dir = os.path.join(base_dir, "Templates")

        self.build_deps = list()
        self.release_monitoring = None

        self.doc_files = list()

    def verify(self):
        print("Verifying %s" % self.package_uri)
        self.file_name = self.package_uri.split("/")[-1]
        self.file_name_full = os.path.abspath(self.file_name)
        print(self.file_name)
        try:
            dloader.download_file(self.package_uri)
            self.sha256sum = dloader.get_sha256sum(self.file_name)
        except Exception as e:
            print(e)
            return False
        return True

    def examine_source(self):
        splits = self.file_name.split(".")
        suffix = "".join(splits[-2:]).replace("bzip2", "bz2")
        # Find out pspec file type
        if suffix.endswith("zip"):
            suffix = "zip"
        self.file_type = suffix

        # Work out the version number
        path, ext = os.path.splitext(self.file_name)
        version = path.split("-")[-1].split(".")[:-1]
        self.version_string = ".".join(version)

        # Package name, including hyphens
        package_name = ("-".join(path.split("-")[:-1])).lower()
        if package_name:
            self.package_name = package_name
        self.component = "PLEASE FILL ME IN"

        print("Package: %s\nVersion: %s" % (self.package_name, self.version_string))

        # Set up temporary
        self.temp_dir = os.path.abspath("./TEMP")
        os.mkdir(self.temp_dir)
        self.current_dir = os.getcwd()

        os.chdir(self.temp_dir)
        os.system('tar xf "%s"' % self.file_name_full)

        known_types = list()

        # Check for certain files..
        for root, dirs, files in os.walk(os.getcwd()):
            depth = root[len(path) + len(os.path.sep):].count(os.path.sep)
            if depth == 3:
                print("bailing")
                # We're currently two directories in, so all subdirs have depth 3
                dirs[:] = []  # Don't recurse any deeper
            for file in files:
                if file in KnownDocFiles:
                    # Append files for pisitools.dodoc ()
                    if file not in self.doc_files:
                        self.doc_files.append(file)
                        print("Added %s" % file)
                if file == "Makefile":
                    self.makefile = True
                if "configure.ac" in file:
                    # Examine this fella for build deps
                    self.build_deps.extend(self.check_build_deps(os.path.join(root, file)))
                if "configure" in file:
                    # Check if we need to employ certain hacks needed in gnome packages
                    f_path = os.path.join(root, file)
                    # Check file type so we only scan text files
                    if mimetypes.guess_type(f_path)[0] == "text/plain":
                        print("Checking %s for use of g-ir-scanner" % f_path)
                        if self.check_is_gnomey(f_path):
                            known_types.append(GNOMEY)
                        else:
                            known_types.append(AUTOTOOLS)
                if (
                    "setup.py" in file
                    or "pyproject.toml" in file
                    or "setup.cfg" in file
                ):
                    # this is a python module.
                    if PYTHON_MODULES not in known_types:
                        known_types.append(PYTHON_MODULES)
                        self.component = "programming.python"
                        self.package_name = f"python-{self.package_name}"
                # Handle python modules respecting PEP517.
                if "pyproject.toml" in file or "setup.cfg" in file:
                    if PEP517 not in known_types:
                        known_types.append(PEP517)
                        pyproject_deps = ["python-build", "python-installer"]
                        if PYTHON_SETUPTOOLS not in known_types:
                            pyproject_deps.append("python-setuptools")
                        self.build_deps.extend(self.extra_build_deps(pyproject_deps))
                # Handle legacy setuptools python modules.
                if "setup.py" in file:
                    if PYTHON_SETUPTOOLS not in known_types and PEP517 not in known_types:
                        known_types.append(PYTHON_SETUPTOOLS)
                        self.build_deps.extend(self.extra_build_deps(["python-setuptools"]))
                if "Makefile.PL" in file or "Build.PL" in file:
                    # This is a perl module
                    known_types.append(PERL_MODULES)
                    self.component = "programming.perl"
                if "BUILD.PL" in file:
                    self.buildpl = True
                if ".cabal" in file:
                    known_types.append(CABAL)
                    self.component = "programming.haskell"
                if ".gemspec" in file:
                    known_types.append(RUBY)
                    self.component = "programming.ruby"
                if "meson.build" in file:
                    known_types.append(MESON)
                    if CMAKE in known_types:
                        known_types.remove(CMAKE)
                if "CMakeLists.txt" in file:
                    if MESON not in known_types:
                        known_types.append(CMAKE)
                if "yarn.lock" in file:
                    known_types.append(YARN)
                if "wscript" in file:
                    known_types.append(WAF)
                if ".pro" in file:
                    known_types.append(QMAKE)
        if ".gem" in self.file_name:
            known_types.append(RUBY_GEMS)
            self.component = "programming.ruby"

        # We may have hit several systems..
        if CMAKE in known_types:
            print("cmake")
            self.compile_type = CMAKE
        elif GNOMEY in known_types:
            print("gnomey")
            self.compile_type = GNOMEY
        elif AUTOTOOLS in known_types:
            print("autotools")
            self.compile_type = AUTOTOOLS
        elif PYTHON_MODULES in known_types:
            print("python")
            self.compile_type = PYTHON_MODULES
        elif PERL_MODULES in known_types:
            print("perl")
            self.compile_type = PERL_MODULES
        elif CABAL in known_types:
            print("cabal")
            self.compile_type = CABAL
        elif RUBY in known_types:
            print("ruby")
            self.compile_type = RUBY
        elif RUBY_GEMS in known_types:
            print("ruby-gem")
            self.compile_type = RUBY_GEMS
        elif MESON in known_types:
            print("meson")
            self.compile_type = MESON
        elif WAF in known_types:
            self.compile_type = WAF
            print("waf")
        elif QMAKE in known_types:
            self.compile_type = QMAKE
            print("qmake")
        elif YARN in known_types:
            self.compile_type = YARN
            self.networking = True
            print("yarn")
        elif PEP517 in known_types:
            self.compile_type = PYTHON_MODULES
            print("PEP517")
        elif PYTHON_SETUPTOOLS in known_types:
            self.compile_type = PYTHON_MODULES
            print("PYTHON_SETUPTOOLS")
        else:
            print("unknown")

        # Clean up on aisle 3
        os.chdir(self.current_dir)
        shutil.rmtree(self.temp_dir)

        # Always delete
        if os.path.exists(self.file_name):
            os.remove(self.file_name)

    @staticmethod
    def check_build_deps(path):
        deps = list()
        with open(path, "r") as read:
            for line in read.readlines():
                line = line.replace("\n", "").replace("\r", "").strip()
                # Currently only handles configure.ac
                if "PKG_CHECK_MODULES" in line:
                    splits = line.split(",")
                    part = splits[1] if len(splits) > 1 else splits[0]
                    part = part.replace("[", "").replace(")", "").replace("]", "")
                    splits = part.strip().split(" ")
                    version_info = None
                    for entry in splits:
                        if entry in ["=", "<=", ">="]:
                            version_info = True
                            continue
                        if version_info:
                            # Can happen, we don't handle variable expansion.
                            version_info = False
                            if "$" in entry:
                                continue
                            deps[-1].version = entry
                            continue
                        if "$" in entry:
                            continue
                        dep = DepObject()
                        dep.name = entry
                        # Check it hasn't been added
                        objs = [x for x in deps if x.name == dep.name]
                        if len(objs) == 0:
                            deps.append(dep)

        return deps

    @staticmethod
    def extra_build_deps(deps):
        extra_deps = list()
        for entry in deps:
            dep = DepObject()
            dep.name = entry
            extra_deps.append(dep)
        return extra_deps

    def create_yaml(self):
        """Attempt creation of a package.yml..."""

        with open("package.yml", "w") as yml:
            mapping = {
                "NAME": self.package_name,
                "VERSION": self.version_string,
                "SOURCE": self.package_uri,
                "SHA256SUM": self.sha256sum,
                "COMPONENT": self.component,
                "HOMEPAGE": self.release_monitoring.homepage or "PLEASE FILL ME IN",
            }

            tmp = (
                """# yaml-language-server: $schema=/usr/share/ypkg/schema/schema.json
name       : %(NAME)s
version    : %(VERSION)s
release    : 1
source     :
    - %(SOURCE)s : %(SHA256SUM)s
homepage   : %(HOMEPAGE)s
license    : GPL-2.0-or-later # CHECK ME
component  : %(COMPONENT)s\n"""
                % mapping
            )

            if self.networking:
                tmp += "\nnetworking : yes\n"

            tmp += """summary    : PLEASE FILL ME IN

description: |
    PLEASE FILL ME IN"""

            total_str = tmp
            setup = None
            build = None
            install = None

            total_str += "\nbuilddeps  :\n"
            if self.build_deps is not None and len(self.build_deps) > 0:
                for dep in self.build_deps:
                    if len(dep.name.strip()) == 0:
                        continue
                    if dep.name in ["python-build", "python-installer", "python-setuptools"]:
                        total_str += "    - %s\n" % dep.name
                        continue
                    total_str += "    - pkgconfig(%s)\n" % dep.name
            if self.compile_type == GNOMEY:
                setup = "%configure --disable-static"
            elif self.compile_type == CMAKE:
                setup = "%cmake_ninja"
                build = "%ninja_build"
                install = "%ninja_install"
            elif self.compile_type == MESON:
                setup = "%meson_configure"
                build = "%ninja_build"
                install = "%ninja_install"
            elif self.compile_type == PYTHON_MODULES:
                setup = ""
                build = "%python3_setup"
                install = "%python3_install"
            elif self.compile_type == PERL_MODULES:
                setup = "%perl_setup"
                build = "%perl_build"
                install = "%perl_install"
            elif self.compile_type == CABAL:
                setup = "%cabal_configure"
                build = "%cabal_build"
                install = "%cabal_install"
            elif self.compile_type == RUBY:
                setup = ""
                build = "%gem_build"
                install = "%gem_install"
            elif self.compile_type == RUBY_GEMS:
                setup = ""
                build = ""
                install = "%gem_install"
            elif self.compile_type == QMAKE:
                setup = "%qmake"
                build = "%make"
                install = "%make_install"
            elif self.compile_type == WAF:
                setup = "%waf_configure"
                build = "%waf_build"
                install = "%waf_install"
            elif self.compile_type == YARN:
                setup = "yarn install"
                build = ""
                install = ""

            if setup is None:
                setup = "%configure"
            if build is None:
                build = "%make"
            if install is None:
                install = "%make_install"

            mapping = {"SETUP": setup, "BUILD": build, "INSTALL": install}
            tmpl = (
                """setup      : |
    %(SETUP)s
build      : |
    %(BUILD)s
install    : |
    %(INSTALL)s
"""
                % mapping
            )
            total_str += "\n" + tmpl

            yml.writelines(total_str.replace("\n\n", "\n"))
            yml.flush()

    @staticmethod
    def check_is_gnomey(path):
        with open(path, "r") as makefile:
            lines = makefile.read()
            if "g-ir-scanner" in lines or "g_ir_scanner" in lines:
                return True
        return False

    def create_monitoring(self):
        self.release_monitoring = get_release_monitoring(
            self.package_name, self.package_uri
        )
        self.release_monitoring.to_yaml("monitoring.yaml")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{sys.argv[0]}: <URI> <PKG-NAME>?")
        sys.exit(-1)

    if len(sys.argv) > 2:
        p = AutoPackage(sys.argv[1], sys.argv[2])
    else:
        p = AutoPackage(sys.argv[1])
    if not p.verify():
        print("Unable to locate given URI")
    else:
        print("Completed verification")
        p.examine_source()
        p.create_monitoring()
        p.create_yaml()
