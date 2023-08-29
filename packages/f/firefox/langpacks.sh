#!/bin/bash
set -e
VER=$1
ARCH="x86_64"
RELURL="https://ftp.mozilla.org/pub/firefox/releases"

if [[ ! $VER =~ ^[0-9]+(\.[0-9]+)*$ ]];
then
  echo "Usage: $0 <version number>"
  echo ""
  echo "Error: missing or invalid Firefox version number"
  exit 1
fi

echo "Processing Firefox langpacks"

URL="${RELURL}/${VER}/linux-${ARCH}/xpi/"

# Ensure we don't have a previous run living here
if [[ -e ff_lang_pack ]]; then
    rm -rvf ff_lang_pack
fi

mkdir ff_lang_pack
pushd ff_lang_pack

echo "mirror ." | lftp "${URL}"

# Inspired largely by Fedora
for i in *.xpi ; do
    ln="$(basename ${i} .xpi)"
    eid="langpack-${ln}@firefox.mozilla.org"
    unzip $i -d "${eid}"
    find "${eid}" -type f | xargs chmod 644
    find "${eid}" | xargs touch --no-dereference --date="@0"
    pushd "${eid}"
    zip -qq -r9mX "../${eid}.xpi" *
    rm ../$i
    popd
    rm -rf "${eid}"
done

popd

# Fully reproducible
tar --sort=name \
    --mtime="@0" \
    --owner=0 --group=0 --numeric-owner \
    -acvf firefox-${VER}-langpacks.tar.zst ff_lang_pack

rm -fr ff_lang_pack

SHASUM=$(sha256sum firefox-${VER}-langpacks.tar.zst)
echo ""
echo "firefox-${VER}-langpacks.tar.zst : ${SHASUM%% *}"

