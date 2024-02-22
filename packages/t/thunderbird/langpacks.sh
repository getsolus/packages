#!/bin/bash
# Insired largely by Fedora
set -e
VER=$1
RELURL="https://ftp.mozilla.org/pub/thunderbird/releases"
ARCH="x86_64"

if [[ ! $VER =~ ^[0-9]+(\.[0-9]+)*$ ]];
then
  echo "Usage: $0 <version number>"
  echo ""
  echo "Error: missing or invalid Thunderbird version number"
  exit 1
fi

WHITE='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${WHITE}Processing Thunderbird langpacks${NC}"

URL="${RELURL}/${VER}/linux-${ARCH}/xpi/"

# Ensure we don't have a previous run living here
if [[ -e thunderbird_langpacks ]]; then
  rm -rf thunderbird_langpacks
fi

mkdir thunderbird_langpacks
pushd thunderbird_langpacks
echo ${URL}
echo "mirror ." | lftp "${URL}"

  for i in *.xpi ; do
    ln="$(basename ${i} .xpi)"
    eid="langpack-${ln}@thunderbird.mozilla.org"
    echo "Processing thunderbird locale: ${ln}"
    unzip -qq $i -d "${eid}"
    find "${eid}" -type f | xargs chmod 00644
    find "${eid}" | xargs touch --no-dereference --date="@0"
    cd "${eid}"
      zip -qq -r9mX "../${eid}.xpi" *
      rm ../$i
    cd ..
    rm -rf "${eid}"
  done

popd

# Fully reproducible
tar --sort=name \
    --mtime="@0" \
    --owner=0 --group=0 --numeric-owner \
    -acvf thunderbird-${VER}-langpacks.tar.zst thunderbird_langpacks

rm -rf thunderbird_langpacks

# Getting sha256sum's
echo "Getting sha256sum for new thunderbird source tarball"
wget ${RELURL}/${VER}/source/thunderbird-${VER}.source.tar.xz
SOURCE_SHASUM=$(sha256sum thunderbird-${VER}.source.tar.xz)
SHASUM=$(sha256sum thunderbird-${VER}-langpacks.tar.zst)

echo ""
echo "${VER}/source/thunderbird-${VER}.source.tar.xz : ${SOURCE_SHASUM%% *}"
echo "thunderbird-${VER}-langpacks.tar.zst : ${SHASUM%% *}"

rm thunderbird-${VER}.source.tar.xz