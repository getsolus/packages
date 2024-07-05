#!/usr/bin/env bash

# Regenerate test file tarball for major libvpx updates or as needed.
# Ask a packager to upload the tarball to sources.getsol.us if it needs to be updated.

set -euo pipefail
set -x

# Check requirements before starting
REQUIREMENTS="curl tar yq zstd"
for i in $REQUIREMENTS; do
    if ! which $i &> /dev/null; then
        echo "Missing requirement: $i. Install it to continue."
        exit 1
    fi
done

tmp_dir=$(mktemp -d)

version="$(yq '.version' package.yml)"
tarball_name="v${version}.tar.gz"
dir="${version}"
test_data_dir="libvpx-test-data"
tmp_archive="libvpx-${version}-test-data.tar.zst"
source_url="$(yq '.source.[0] | to_entries | .[0].key' package.yml)"

pushd "${tmp_dir}"

# Download the first source found in the build recipe
curl -S -L -o "${tarball_name}" "${source_url}"

mkdir -pv "${dir}"
tar xf "${tarball_name}" -C "${dir}" --strip-components=1
rm "${tarball_name}"

# Download test files
pushd "${dir}"
mkdir -pv "${test_data_dir}"
./configure --enable-unit-tests
LIBVPX_TEST_DATA_PATH="${test_data_dir}" make testdata

# Create a reproducible tarball
tar --sort=name --mtime="@0" --owner=0 --group=0 --numeric-owner -acvf ../"${tmp_archive}" "${test_data_dir}"
popd
archive_checksum=$(sha256sum "${tmp_archive}")
archive_name="libvpx-test-data-${archive_checksum:0:16}.tar.zst"

popd
mv "${tmp_dir}/${tmp_archive}" "${archive_name}"

echo "Created ${archive_name}"
echo "${archive_name} : ${archive_checksum%% *}"

rm -fr "${tmp_dir}"
