#!/bin/bash

VERSION="60.3.2"
ARCH="x86_64"
URL="https://ftp.mozilla.org/pub/thunderbird/releases/${VERSION}/linux-${ARCH}/xpi/"

# Ensure we don't have a previous run living here
if [[ -e lang_pack ]]; then
    rm -rvf lang_pack
fi

mkdir lang_pack

pushd lang_pack

echo "mirror ." | lftp "${URL}"

# Insired largely by Fedora
for i in *.xpi ; do
    ln="$(basename ${i} .xpi)"
    eid="langpack-${ln}@thunderbird.mozilla.org"
    unzip $i -d "${eid}"
    find "${eid}" -type f | xargs chmod 644
    pushd "${eid}"
    zip -qq -r9mX "../${eid}.xpi" *
    rm ../$i
    popd
    rm -rf "${eid}"
done

popd

tar cvfJ thunderbird-${VERSION}-langpacks.tar.xz lang_pack
