#!/usr/bin/env bash

# Regenerate test file tarball for major libvpx updates or as needed.
# Ask a packager to upload the tarball to sources.getsol.us if it needs to be updated.

set -euo pipefail

# Check requirements before starting
REQUIREMENTS="curl tar yq zstd"
for i in $REQUIREMENTS; do
    if ! which $i &> /dev/null; then
        echo "Missing requirement: $i. Install it to continue."
        exit 1
    fi
done

tarball_name="v$(yq '.version' package.yml).tar.gz"
dir="$(yq '.version' package.yml)"
test_data_dir="libvpx-test-data"

# Download the first source found in the build recipe
curl -S -L -o "${tarball_name}" $(yq '.source.[0] | to_entries | .[0].key' package.yml)

mkdir -pv "${dir}"
tar xf "${tarball_name}" -C "${dir}" --strip-components=1
rm "${tarball_name}"

# Download test files
pushd "${dir}"
mkdir -pv "${test_data_dir}"
./configure --enable-unit-tests
LIBVPX_TEST_DATA_PATH="${test_data_dir}" make testdata

# Create a reproducible tarball
tar --sort=name --mtime="@0" --owner=0 --group=0 --numeric-owner -acvf ../"${test_data_dir}".tar.zst "${test_data_dir}"
popd

echo "Created "${test_data_dir}".tar.zst"

rm -fr "${dir}"
