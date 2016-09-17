#!/usr/bin/env python3
#
# abireport.py - part of autospec
# Copyright (C) 2016 Intel Corporation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Generate a symbols file from all shared libraries encountered, enabling
# a consistent ABI report for every build. We ensure that everything is
# appropriately sorted, in that a diff only occurs when the shared libraries
# in the package themselves actually change too.

import subprocess
import re
import os
import sys
import util
import shutil

valid_dirs = ["/usr/lib", "/usr/lib64", "/usr/lib32", "/lib", "/lib32", "/lib64"]

# For determining .so's
reg = re.compile(r".* ELF (64|32)\-bit LSB shared object,")

# All dynamic binaries
valid_dyn = re.compile(r".* ELF (64|32)\-bit LSB (shared object|executable),")

# shared-lib matcher
shared_lib = re.compile(r".*Shared library: \[(.*)\].*")

wanted_symbol_types = ["A", "T"]

ignored_symbols = [
    "__bss_start",
    "_edata",
    "_end",
    "_fini",
    "_init",
]


def get_output(cmd):
    try:
        o = subprocess.getoutput(cmd)
        return o
    except Exception as e:
        print("Error: %s" % e)


def get_soname(path):
    cmd = "objdump -p \"{}\"|grep SONAME".format(path)
    try:
        line = get_output(cmd)
        if "SONAME" not in line:
            return None
        line = line.strip()
        spl = line.split()[1]
        return spl
    except Exception:
        return None


def get_shared_dependencies(path):
    ''' Return the shared dependencies for a given path '''
    ret = set()
    cmd = "readelf -d {}".format(path)

    for line in get_output(cmd).split("\n"):
        line = line.strip()
        shared = shared_lib.match(line)
        if shared is None:
            continue
        ret.add(shared.group(1))

    return ret


def get_all_dependencies(path):
    ''' Determine all dependencies in the given path '''

    deps = set()

    sonames = set()
    examine = set()

    for root, dirs, files in os.walk(path):
        for file in files:
            fpath = os.path.join(root, file)
            if not is_dynamic_binary(fpath):
                continue
            # Encountered a valid dynamic linked object
            if is_file_valid(fpath):
                # We must account for *all* internal symbols due to rpaths and
                # overriding of LD_LIBRARY_PATH
                soname = get_soname(fpath)
                if soname is not None:
                    sonames.add(soname)
            if is_dynamic_binary(fpath):
                examine.add(fpath)

    for path in examine:
        current_deps = get_shared_dependencies(path)
        # Ensure we don't add a dependency on an internally provided symbol
        deps.update(set(filter(lambda s: s not in sonames, current_deps)))

    return deps


def get_file_magic(path):
    ''' Return the 'magic' for a given path '''
    cmd = "file \"{}\"".format(path)
    try:
        line = get_output(cmd).split("\n")[0]
        return line.strip()
    except Exception:
        return None


def is_dynamic_binary(path):
    ''' Determine if a given path is a dynamic binary '''
    if not os.path.exists(path) or not os.path.isfile(path):
        return False
    mg = get_file_magic(path)
    if not mg:
        return False
    if valid_dyn.match(mg):
        return True
    return False


def is_file_valid(path):
    if not os.path.exists(path) or os.path.islink(path):
        return False
    mg = get_file_magic(path)
    if not mg:
        return False
    if reg.match(mg):
        return True
    return False


def dump_symbols(path):
    cmd = "nm --defined-only -g --dynamic \"{}\"".format(path)
    lines = None

    ret = set()

    try:
        lines = get_output(cmd)
    except Exception as e:
        print("Fatal error inspecting {}: {}".format(path, e))
        sys.exit(1)
    for line in lines.split("\n"):
        line = line.strip()

        spl = line.split()
        if len(spl) != 3:
            continue
        sym_type = spl[1]
        sym_id = spl[2]

        if sym_type not in wanted_symbol_types:
            continue
        if sym_id in ignored_symbols:
            continue
        ret.add(sym_id)
    return ret


def purge_tree(tree):
    if not os.path.exists(tree):
        return
    try:
        shutil.rmtree(tree)
    except Exception as e:
        util.print_fatal("Cannot remove tree: {}".format(e))
        sys.exit(1)


def truncate_file(path):
    if not os.path.exists(path):
        return
    with open(path, "r+", encoding="utf-8") as trunc:
        trunc.truncate()


def examine_abi(download_path):
    download_path = os.path.abspath(download_path)

    if not os.path.exists(download_path):
        util.print_fatal("Work directory does not exist, aborting")
        sys.exit(1)

    old_dir = os.getcwd()

    eopkgs = set()
    for item in os.listdir(download_path):
        if item.endswith(".eopkg"):
            eopkgs.add(os.path.basename(item))

    if len(eopkgs) == 0:
        util.print_fatal("No usable eopkgs found, aborting")
        sys.exit(1)

    extract_dir = os.path.abspath(os.path.join(download_path, "__extraction"))
    purge_tree(extract_dir)

    try:
        os.makedirs(extract_dir)
    except Exception as e:
        util.print_fatal("Cannot create extraction tree: {}".format(e))
        sys.exit(1)

    os.chdir(extract_dir)

    # Extract all those rpms to our current directory
    try:
        for eopkg in eopkgs:
            cmd = "unpisi \"{}\" 2>/dev/null".format(os.path.join(download_path, eopkg))
            subprocess.check_call(cmd, shell=True)
    except Exception as e:
        util.print_fatal("Error extracting eopkgs: {}".format(e))

    # eopkg extraction root
    source_dir = os.path.join(extract_dir, "install")
    os.chdir(source_dir)
    collected_files = set()

    # Places we expect to find shared libraries
    for check_path in valid_dirs:
        if check_path[0] == '/':
            check_path = check_path[1:]

        dirn = os.path.join(source_dir, check_path)
        if not os.path.isdir(dirn):
            continue

        for file in os.listdir(dirn):
            f = os.path.basename(file)

            clean_path = os.path.abspath(os.path.join(dirn, f))
            if not is_file_valid(clean_path):
                continue
            collected_files.add(clean_path)

    abi_report = dict()

    # Now examine these libraries
    for library in sorted(collected_files):
        soname = get_soname(library)
        if not soname:
            util.print_fatal("Failed to determine soname of valid library!")
            sys.exit(1)
        symbols = dump_symbols(library)
        if symbols and len(symbols) > 0:
            if soname not in abi_report:
                abi_report[soname] = set()
            abi_report[soname].update(symbols)

    report_file = os.path.join(download_path, "symbols")

    if len(abi_report) > 0:
        # Finally, write the report
        report = open(report_file, "w", encoding="utf-8")
        for soname in sorted(abi_report.keys()):
            for symbol in sorted(abi_report[soname]):
                report.write("{}:{}\n".format(soname, symbol))

        report.close()
    else:
        truncate_file(report_file)

    # Write the library report
    lib_deps = get_all_dependencies(source_dir)
    report_file = os.path.join(download_path, "used_libs")
    if len(lib_deps) > 0:
        report = open(report_file, "w", encoding="utf-8")
        for soname in sorted(lib_deps):
            report.write("{}\n".format(soname))
        report.close()
    else:
        truncate_file(report_file)

    os.chdir(old_dir)
    purge_tree(extract_dir)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        examine_abi(sys.argv[1])
    else:
        examine_abi(".")
