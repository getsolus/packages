#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright © 2025 Serpent OS Developers
#
# SPDX-License-Identifier: MPL-2.0

import argparse
import atexit
import glob
import os
import shutil
import sys
import unittest
from importlib.metadata import Distribution

from packaging.requirements import Requirement
from ruamel.yaml import YAML
from pisi.api import fetch
from pisi.package import Package


SOLUS_RECIPE_FILE = ["package.yml", "package.yaml"]

parser = argparse.ArgumentParser()
parser.add_argument("location", type=str, nargs='?', help="Location of .egg-info or .dist-info directory")

eopkg_already_exists = False


@staticmethod
def get_dependencies(dependencies: list, env=None) -> list:
    sanitized = []

    if dependencies is None:
        return sanitized

    for dep in dependencies:
        req = Requirement(dep)
        if not req.extras:
            if req.marker:
                mark = req.marker
                if mark.evaluate(environment=env) is True:
                    sanitized.append(req.name)
                    continue
            else:
                sanitized.append(req.name)
    return sanitized


def usage(msg=None, ex=1):
    if msg:
        print(msg, file=sys.stderr)
    else:
        parser.print_help()
    sys.exit(ex)


def parse_recipe(path) -> tuple:
    yaml = YAML()
    with open(path, 'r') as file:
        data = yaml.load(file)

    name = data.get('name')
    version = data.get('version')
    release = data.get('release')

    return f"{name}-{version}-{release}-1-x86_64.eopkg", name


def init_recipe_parse_path():
    for i in SOLUS_RECIPE_FILE:
        if os.path.exists(i):
            eopkg_path, package_name = parse_recipe(i)
            if not os.path.exists(eopkg_path):
                fetch([package_name])
            else:
                global eopkg_already_exists
                eopkg_already_exists = True
            extract_eopkg(eopkg_path)
            find_python_files("install")


def find_python_files(path):
    target_dirs = [".egg-info", ".dist-info"]

    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            for substring in target_dirs:
                if substring in dir_name:
                    print_dependencies(os.path.join(root, dir_name))


def extract_eopkg(eopkg=str):

    package = Package(eopkg)

    if not os.path.exists("install"):
        os.makedirs("install")

    package.extract_pisi_files(".")
    package.extract_dir("comar", ".")
    if not os.path.exists(os.path.join(".", "install")):
        os.makedirs(os.path.join(".", "install"))
    package.extract_install(os.path.join(".", "install"))
    if os.listdir("install") == []:
        os.rmdir("install")


def init_location_path(path):
    if not (os.path.exists(os.path.join(path, 'METADATA')) or os.path.exists(os.path.join(path, 'PKG-INFO'))):
        usage("Unable to find PKG-INFO or METADATA files in specified directory")
    print_dependencies(path)


def find_mismatched_elements(list1, list2):
    normalized_list1 = {item.lower().removeprefix("python-").replace("-", "_") for item in list1}
    normalized_list2 = {item.lower().replace("-", "_") for item in list2}

    return normalized_list1 ^ normalized_list2


def check_against_rundeps(deps):
    yaml = YAML()
    with open("package.yml", "r") as file:
        data = yaml.load(file)
        rundeps = data.get("rundeps", [])
        if rundeps:
            missing_elements = find_mismatched_elements(rundeps, deps)

            print("Required Deps:", deps)
            print("Current Run Deps:", rundeps)
            print("Mismatched dependencies:", missing_elements)
            print("NOTE: The 'python-' prefix is removed and '-' '_' are equivalently compared.")


def print_dependencies(path):
    dependencies = Distribution.at(path).requires

    printed_deps = get_dependencies(dependencies)

    if printed_deps:
        check_against_rundeps(printed_deps)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.location and not os.path.exists(args.location):
        usage()

    if not any(os.path.exists(path) for path in SOLUS_RECIPE_FILE) and args.location is None:
        usage(msg="Expects a package.yml in current directory or pass a .egg-info or .dist-info path")

    if args.location is None:
        init_recipe_parse_path()
    else:
        init_location_path(args.location)


# Cleanup on exit
@atexit.register
def cleanuponexit():
    if eopkg_already_exists is False:
        matched_files = [file_path for file_path in glob.glob("*.eopkg")]
        for i in matched_files:
            os.unlink(i)
    if os.path.exists("install"):
        shutil.rmtree("install")
    if os.path.exists("files.xml"):
        os.unlink("files.xml")
    if os.path.exists("metadata.xml"):
        os.unlink("metadata.xml")


class Tests(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(get_dependencies(['six']), ['six'])

    def test_empty_list(self):
        self.assertEqual(get_dependencies([]), [])

    def test_excludes_version(self):
        self.assertEqual(get_dependencies(['six>=6.9']), ['six'])

    def test_excludes_extras(self):
        list1 = ['MarkupSafe>=2.0', 'Babel>=2.7; extra == "i18n"']
        self.assertEqual(get_dependencies(list1), ['MarkupSafe'])

    def test_excludes_extras_no_deps(self):
        self.assertEqual(get_dependencies(['Babel>=2.7; extra == "i18n"', 'pytest; extra == "testing"']), [])

    def test_excludes_extras_comprehensive(self):
        list2 = ['MarkupSafe>=0.9.2', 'Babel; extra == "babel"',
                 'lingua; extra == "lingua"', 'pytest; extra == "testing"']
        self.assertEqual(get_dependencies(list2), ['MarkupSafe'])

    def test_ignore_satisfied_evaluate_markers(self):
        env = {'python_version': '3.11'}
        list3 = ["tomli>=1.2.2; python_version < '3.11'", 'pluggy>=1.0.0']
        self.assertEqual(get_dependencies(list3, env), ['pluggy'])

    def test_included_unsatisified_evaluate_markers(self):
        env = {'python_version': '3.11'}
        list4 = ['pluggy', "tomli>=1.2.2; python_version < '3.12'"]
        self.assertEqual(get_dependencies(list4, env), ['pluggy', 'tomli'])

    def test_comprehensive1(self):
        env = {'python_version': '3.11'}
        list5 = ['pytest; extra == "testing"', 'editables>=0.3', 'packaging>=21.3',
                 'pathspec>=0.10.1', 'pluggy>=1.0.0', "tomli>=1.2.2; python_version < '3.12'", 'trove-classifiers']
        self.assertEqual(get_dependencies(list5, env), ['editables', 'packaging', 'pathspec',
                                                        'pluggy', 'tomli', 'trove-classifiers'])

    def test_comprehensive2(self):
        list6 = ["brotli; implementation_name == 'cpython'", "brotlicffi; implementation_name != 'cpython'", 'certifi', 'mutagen', 'pycryptodomex', 'requests<3,>=2.32.2', 'urllib3<3,>=1.26.17', 'websockets>=12.0', "build; extra == 'build'", "hatchling; extra == 'build'", "pip; extra == 'build'", "setuptools>=71.0.2; extra == 'build'", "wheel; extra == 'build'", "curl-cffi!=0.6.*,<0.8,>=0.5.10; (os_name != 'nt' and implementation_name == 'cpython') and extra == 'curl-cffi'", "curl-cffi==0.5.10; (os_name == 'nt' and implementation_name == 'cpython') and extra == 'curl-cffi'", "pre-commit; extra == 'dev'", "yt-dlp[static-analysis]; extra == 'dev'", "yt-dlp[test]; extra == 'dev'", "py2exe>=0.12; extra == 'py2exe'", "pyinstaller>=6.7.0; extra == 'pyinstaller'", "cffi; extra == 'secretstorage'", "secretstorage; extra == 'secretstorage'", "autopep8~=2.0; extra == 'static-analysis'", "ruff~=0.5.0; extra == 'static-analysis'", "pytest~=8.1; extra == 'test'"]  # noqa: E501 There is no sane way to split all of this up into short enough lines
        self.assertEqual(get_dependencies(list6), ['brotli', 'certifi', 'mutagen', 'pycryptodomex',
                                                   'requests', 'urllib3', 'websockets'])
