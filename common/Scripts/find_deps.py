#!/usr/bin/env python2
from pisi.db.filesdb import FilesDB
import pisi.api
import magic
import os
import re
import subprocess

valid_dyn = ""

v_dyn = re.compile(r"ELF (64|32)\-bit LSB shared object,")
v_bin = re.compile(r"ELF (64|32)\-bit LSB executable,")
shared_lib = re.compile(r".*Shared library: \[(.*)\].*")
r_path = re.compile(r".*Library rpath: \[(.*)\].*")

def accumulate_dependencies(path, emul32=False):
    output = subprocess.check_output("/usr/bin/readelf -d {}".format(path), shell=True)

    check_deps = set()
    r_paths = set()

    valid_libs = set()

    if emul32:
        valid_libs.update(["/usr/lib32"])
    else:
        # Currently on Solus this is the same thing as /usr/lib.
        valid_libs.update(["/usr/lib64"])

    for line in output.split("\n"):
        line = line.strip()
        g = shared_lib.match(line)
        if g:
            check_deps.add(g.group(1))
        r = r_path.match(line)
        if r:
            r_paths.add(r.group(1))

    print("Deps: {}".format(", ".join(check_deps)))

    dirname = os.path.dirname(path)

    filter_deps = [x for x in check_deps for y in r_paths if os.path.exists(os.path.join(y, x)) or os.path.exists(os.path.join(dirname, x))]
    print("Filtered by rpath: {}".format(", ".join(filter_deps)))

    print("Got %d of rpath:" % len(filter_deps))

    ret_deps = filter(lambda s: s not in filter_deps, check_deps)
    print("Remaining deps: {}".format(", ".join(ret_deps)))

    full_paths = [os.path.join(y,x) for x in ret_deps for y in valid_libs if os.path.exists(os.path.join(y,x))]
    print("Full paths is now: {}".format(", ".join(full_paths)))
    return full_paths

def is_dynamic_binary(path):
    if not os.path.exists(path) or not os.path.isfile(path):
        return (False,False)
    try:
        mg = magic.from_file(path)
    except Exception, e:
        return (False,False)
    emul32 = mg.startswith("ELF 32")
    if v_bin.match(mg):
        return (True,emul32)
    if v_dyn.match(mg):
        return (True,emul32)
    return (False,False)

def clean_path(p):
    if not p[0] == '/':
        return "/%s" % p

def main():
    le_files = set()

    packages = ["gedit"]

    for pkg in packages:
        (stuff,files,repo) = pisi.api.info_name(pkg, True)

        deps = set()
        for f in files.list:
            f = clean_path(f.path)

            (dyn,emul32) = is_dynamic_binary(f)
            if not dyn:
                continue
            deps.update(accumulate_dependencies(f, emul32))

        print("Full binary dependencies for %s" % pkg)
        for dep in deps:
            print("  -> {}".format(dep))

if __name__ == "__main__":
    main()

