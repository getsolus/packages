#!/usr/bin/env python3

import logging
import re
import subprocess
import urllib.request

from pathlib import Path

logger = logging.getLogger("update-chromium.py")
logging.basicConfig(level=logging.INFO)

packageyml_recipe = Path("./package.yml")
if not packageyml_recipe.is_file():
    logger.error("This script needs to be ran in the same directory as a package.yml")
    exit(1)

# TODO: maybe make this follow path
yq = Path("/usr/bin/yq")
if not yq.is_file():
    logger.error("yq binary not found, please install it from your package manager")
    exit(1)

# TODO: maybe make this follow path
git = Path("/usr/bin/git")
if not git.is_file():
    logger.error("git binary not found, please install it from your package manager")
    exit(1)

qtwebengine_version = subprocess.run([yq, ".version", packageyml_recipe], capture_output=True, check=True).stdout.decode().rstrip()
logger.info(f"qtwebengine version: {qtwebengine_version}")

qtwebengine_url = f"https://invent.kde.org/qt/qt/qtwebengine/-/raw/v{qtwebengine_version}/CHROMIUM_VERSION"
with urllib.request.urlopen(qtwebengine_url) as qtwebengine_request:
    if qtwebengine_request.getcode() != 200:
        logger.error("Request code :" + qtwebengine_request.getcode())
        exit(1)
    qtwebengine_response = qtwebengine_request.read().decode()

response_regex = re.compile('(?:Based on Chromium version: *)([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*)')
chromium_version = re.search(response_regex, qtwebengine_response).group(1)
if chromium_version is None:
    logger.error("Chromium version not found")
    exit(1)

chromium_version_major = chromium_version.split(".")[0]
logger.info(f"Chromium major version detected as v{chromium_version_major}")

chromium_git = "https://invent.kde.org/qt/qt/qtwebengine-chromium.git"
chromium_git_output = subprocess.run([git, "ls-remote", chromium_git, f"{chromium_version_major}-based"], capture_output=True, check=True).stdout.decode().rstrip()

commit_regex = re.compile('^([a-f0-9]*)')
chromium_commit = re.search(commit_regex, chromium_git_output).group(1)
if chromium_commit is None:
    logger.error("Chromium commit not detected")
    exit(1)

logger.info(f"Latest chromium commit for v{chromium_version_major} branch: {chromium_commit}")

upstreams_output = \
f"""##@@BEGIN_UPSTREAMS
    - git|{chromium_git}: {chromium_commit}
##@@END_UPSTREAMS"""

# Read the package.yml so we can modify it
with open(packageyml_recipe, 'r') as file:
    packageyml_content = file.read()

# Replace the upstreams section
packageyml_content = re.sub('##@@BEGIN_UPSTREAMS?(.*?)##@@END_UPSTREAMS', upstreams_output, packageyml_content, flags=re.DOTALL)

logger.info("Updating package.yml")
with open(packageyml_recipe, "w") as f:
    f.write(packageyml_content)

logger.info("Success!")
