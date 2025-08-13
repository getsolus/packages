#!/usr/bin/env python3

import hashlib
import os.path
from pathlib import Path
import re
import shutil
from string import Template
import subprocess
import sys

def print_usage():
    print("This script should be ran with only a single argument provided")
    print("That argument should be in the format $number.$number.$number, with or without a following esr string")
    print("Valid examples:")
    print("./update.py 141.0.1")
    print("./update.py 128.1.0esr")

n = len(sys.argv)

if n != 2:
    print_usage()
    exit(1)

version = sys.argv[1]

version_regex = re.compile('[0-9]*\.[0-9]*\.[0-9]*(?:esr)?$')
if not version_regex.match(version):
    print_usage()
    exit(1)

packageyml_recipe = Path("./package.yml")
if not packageyml_recipe.is_file():
    print("This script needs to be ran in the same directory as a package.yml")
    exit(1)

# TODO: maybe make this follow path
lftp = Path("/usr/bin/lftp")
if not lftp.is_file():
    print("lftp binary not found, please install it from your package manager")
    exit(1)


arch = "x86_64"
release_url = "https://ftp.mozilla.org/pub/firefox/releases"
xpi_url = f"{release_url}/{version}/linux-{arch}/xpi/"

print ("Processing Firefox langpacks")

langpack_dir = Path("./tmp_lang_pack")
if langpack_dir.exists():
    print("Deleting temporary directory from previous run")
    shutil.rmtree(langpack_dir)

print("Creating temporary directory for langpacks")
langpack_dir.mkdir()

print("Downloading langpacks from source")
lftp_mirror = subprocess.run([lftp, "-c", f"open {xpi_url}; mirror . {langpack_dir}"], check=True)

upstreams_output = \
"""##@@BEGIN_UPSTREAMS
"""

upstream_template = Template(\
"""    - ${xpi_url}${xpi}.xpi#${eid} : ${hash}
""")

xpi_list = sorted(list(langpack_dir.glob("*.xpi")))
for xpi in xpi_list:
    base = os.path.basename(xpi).removesuffix(".xpi")
    eid = f"langpack-{base}@firefox.mozilla.org.xpi"
    # Hash it!
    with open(xpi, 'rb', buffering=0) as f:
        checksum = hashlib.file_digest(f, 'sha256').hexdigest()
    upstream = upstream_template.substitute(xpi_url = xpi_url,
                                            xpi = base,
                                            eid = eid,
                                            hash = checksum)
    upstreams_output += upstream

upstreams_output += "##@@END_UPSTREAMS"

# Read the package.yml so we can modify it
with open(packageyml_recipe, 'r') as file:
    packageyml_content = file.read()

# Replace the upstreams section
packageyml_content = re.sub('##@@BEGIN_UPSTREAMS?(.*?)##@@END_UPSTREAMS', upstreams_output, packageyml_content, flags=re.DOTALL)

# Update the version string

version_template = Template(\
"""##@@BEGIN_VERSION
version     : "${version}"
##@@END_VERSION""")

version_output = version_template.substitute(version = version)

# Replace version section
packageyml_content = re.sub('##@@BEGIN_VERSION?(.*?)##@@END_VERSION', version_output, packageyml_content, flags=re.DOTALL)

print("Updating package.yml")
with open(packageyml_recipe, "w") as f:
    f.write(packageyml_content)

print("Success!")
