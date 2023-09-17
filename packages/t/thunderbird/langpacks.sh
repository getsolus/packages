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

# Ensure we don't have a previous run living here
rm -rf thunderbird_langpacks
mkdir thunderbird_langpacks
cd thunderbird_langpacks

  wget --quiet -r -np -l1 -nd -A xpi $RELURL/$VER/linux-$ARCH/xpi/

  for i in *.xpi ; do
    ln="$(basename ${i} .xpi)"
    eid="langpack-${ln}@thunderbird.mozilla.org"
    echo "Processing thunderbird locale: ${ln}"
    unzip -qq $i -d "${eid}"
    find "${eid}" -type f | xargs chmod 00644
    cd "${eid}"
      zip -qq -r9mX "../${eid}.xpi" *
      rm ../$i
    cd ..
    rm -rf "${eid}"
  done

  echo "Creating thunderbird-$VER-langpacks.tar.xz..."
  tar cJf ../thunderbird-$VER-langpacks.tar.xz *.xpi

cd ..

rm -rf thunderbird_langpacks

SHASUM=$(sha256sum thunderbird-$VER-langpacks.tar.xz)
echo ""
echo "thunderbird-$VER-langpacks.tar.xz : ${SHASUM%% *}"

