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


  echo -e "${WHITE}Processing Lightning langpacks${NC}"

  LOCALES=`curl -f $RELURL/$VER/linux-$ARCH/ | grep "a href"|sed -e "s|.*/\([^/]*\)/\".*|\1|"|tail -n+2 |grep -v xpi`
  #echo $LOCALES
  LOCALE_COUNT=`echo $LOCALES| tr ' ' '\n' | wc -l`
  LOCALE_NUM=0
  for lang in $LOCALES; do
    LOCALE_NUM=$((LOCALE_NUM+1))
    echo -e "${WHITE}Processing calendar locale: $lang ($LOCALE_NUM/$LOCALE_COUNT)${NC}"
    mkdir -p extracted_lightning
    mkdir -p calendar-locales
    #echo Downloading TB binary for locale: $lang
    wget --quiet $RELURL/$VER/linux-$ARCH/$lang/thunderbird-$VER.tar.bz2

    cd extracted_lightning
      tar -xf ../thunderbird-$VER.tar.bz2 thunderbird/distribution/extensions/\{e2fda1a4-762b-4020-b5ad-a41df1933103\}.xpi
      set +e
      unzip -qq thunderbird/distribution/extensions/\{e2fda1a4-762b-4020-b5ad-a41df1933103\}.xpi
      set -e
      LIGHTNING_VERSION=`cat app.ini |grep "^Version="|sed -e 's/Version=//'`
      BUILD_ID=`cat app.ini |grep "^BuildID="|sed -e 's/BuildID=//'`
      MAX_VERSION=`cat app.ini |grep MaxVersion|sed -e s/MaxVersion=//`
      MIN_VERSION=`cat app.ini |grep MinVersion|sed -e s/MinVersion=//`
      rm -rf thunderbird
      mkdir -p ../calendar-locales/chrome
      cp -r chrome/calendar-$lang ../calendar-locales/chrome
      cp -r chrome/lightning-$lang ../calendar-locales/chrome
    cd -

    cd calendar-locales
    # create manifest
    cat > manifest.json <<EOL
{
  "languages": {
    "$lang": {
      "chrome_resources": {
        "calendar": "chrome/calendar-$lang/locale/$lang/calendar/",
        "lightning": "chrome/lightning-$lang/locale/$lang/lightning/"
      },
      "version": "$LIGHTNING_VERSION"
    }
  },
  "applications": {
    "gecko": {
      "strict_min_version": "$MIN_VERSION",
      "id": "langpack-cal-$lang@lightning.mozilla.org",
      "strict_max_version": "$MAX_VERSION"
    }
  },
  "langpack_id": "$lang",
  "version": "$LIGHTNING_VERSION$BUILD_ID",
  "name": "$lang Language Pack Calendar",
  "manifest_version": 2,
  "sources": {
    "browser": {
      "base_path": "browser/"
    }
  },
  "author": "Mozilla.cz (contributors: Pavel Cvrček, Pavel Franc, Michal Stanke, Michal Vašíček)",
  "description": "Language pack for Thunderbird for $lang, this was repacked by Solus package maintainer from original binaries."
}

EOL
    zip --quiet -r ../langpack-cal-$lang@lightning.mozilla.org.xpi *
    cd -
    rm -rf calendar-locales
    rm -rf extracted_lightning

    rm -f thunderbird-$VER.tar.bz2
  done

  echo "Creating thunderbird-$VER-lightning-langpacks.tar.xz..."
  tar cJf ../thunderbird-$VER-langpacks.tar.xz *.xpi

cd ..

rm -rf thunderbird_langpacks

SHASUM=$(sha256sum thunderbird-$VER-langpacks.tar.xz)
echo ""
echo "thunderbird-$VER-langpacks.tar.xz : ${SHASUM%% *}"

