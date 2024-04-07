#!/usr/bin/env python3

import os
import subprocess
import sys

import pisi.api

blacklist = (
    "/lib/linux-gate.",
    "/lib/libm.",
    "/lib/ld-linux.",
    "/lib/libc.",
    "/lib/librt.",
    "linux-gate.so.1",
    "/lib/libpthread.",
    "/lib/libdl.",
)


def package_for_file(filename):
    return pisi.api.search_file(filename)


def blacklisted(filename):
    if not filename.startswith("/"):
        filename = f"/{filename}"
    for f in blacklist:
        if f in filename:
            return True
    return False


def ldd(filename):
    if "usr/share" in filename:
        return

    ldd = subprocess.getoutput(f"ldd {filename}")

    for line in ldd.split("\n"):
        line = line.replace("\n", "").replace("\r", "").strip()
        if line == "":
            continue
        splits = line.split("=>")
        sourceLib = splits[0].strip()
        if len(splits) > 1:
            sourceLib = splits[1].strip().split(" ")[0]
        else:
            sourceLib = sourceLib.split(" ")[0].strip()

        # Skip blacklisted
        if blacklisted(sourceLib):
            continue

        if os.path.exists(sourceLib):
            dep = package_for_file(sourceLib)

            if len(dep) > 0:
                # Circular dependencies are ugly :p
                if dep[0][0] == sys.argv[1]:
                    break
                # Check its not accounted for
                if not dep[0][0] in dependsOn:
                    dependsOn[dep[0][0]] = f"/{dep[0][1][0]}"


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} package_name")
        sys.exit(1)

    pkg = sys.argv[1]
    try:
        meta, files, other = pisi.api.info_name(pkg, True)
    except Exception:
        print(f"Could not find package: {pkg}")
        sys.exit(1)

    dependsOn = dict()

    for file in files.list:
        filename = file.path
        if not filename.startswith("/"):
            filename = f"/{filename}"

        if hasattr(file, "type"):
            if file.type == "executable":
                ldd(filename)
            elif file.type == "library" and ".so" in filename:
                ldd(filename)
        else:
            if ".so" in filename:
                ldd(filename)

    print("[ Dependencies ]")
    for dep in dependsOn:
        print(f"Depends on {dependsOn[dep]} from {dep}")

    print("\n[ XML Dependencies ]")
    print("<RuntimeDependencies>")
    for dep in dependsOn:
        print(f"    <Dependency>{dep}</Dependency>")
    print("</RuntimeDependencies>")

    # Suggest build dependencies
    print("\n[XML Build Dependencies]")
    print("<BuildDependencies>")
    for dep in dependsOn:
        package = f"{dep}-devel"
        try:
            subject = pisi.api.info_name(package, True)
            print(f"    <Dependency>{package}</Dependency>")
        except Exception:
            print(f"    <!-- Info: no {package} package - consider splitting -->")
    print("</BuildDependencies>")
