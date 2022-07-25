#!/bin/sh

# Requires notify-send.

# Script to determine whether a published tag has completed on the build server and gives you a notification whether it has completed or failed.
# Additionally, if a package successfully builds it will then check if it gets successfully indexed into the repo.

TAG=$(.././common/Scripts/gettag.py package.yml)
BUILDSERVER_URL="https://build.getsol.us"

# Check it's actually been published first.
if [[ ! $(curl -s $BUILDSERVER_URL | grep "${TAG}") ]] ; then
    echo "${TAG} not found on build queue, has it been published?"
    exit
fi

# Get the latest build-id for the $TAG
BUILDID=$(curl -s $BUILDSERVER_URL | grep -B 1 "${TAG}" | grep -o '[0-9]*' | sort -nr | head -1)
echo "Build ID: ${BUILDID} | Tag: ${TAG}"

# Look for build-ok from the build id
while [[ ! $(curl -s $BUILDSERVER_URL | grep -A 4 ${BUILDID} | grep build-ok) ]] ; do

    # Don't DoS the server
    sleep 20

    # Check if the build has failed
    if [[ $(curl -s $BUILDSERVER_URL | grep -A 4 ${BUILDID} | grep build-failed) ]] ; then
        notify-send -u critical "${TAG} failed on the build server!" -t 0
        paplay /usr/share/sounds/freedesktop/stereo/suspend-error.oga
        exit 1
    fi
done

echo "Build succeeded on the buildserver! Waiting for it to be indexed..."

### Now that it's built make sure it gets indexed into the repo.

# Setup for index check
INDEX_SHA_URL="https://mirrors.rit.edu/solus/packages/unstable/eopkg-index.xml.xz.sha1sum"
INDEX_XZ_URL="https://mirrors.rit.edu/solus/packages/unstable/eopkg-index.xml.xz"
INDEX_SHA=$(curl -s $INDEX_SHA_URL)
curl -s $INDEX_XZ_URL -o /tmp/unstable-index.xml.xz
unxz /tmp/unstable-index.xml.xz

# Downloads and extracts the new index if the sha sum has changed.
download_extract_index_if_changed() {
    NEW_INDEX_SHA=$(curl -s $INDEX_SHA_URL)

    if [[ $NEW_INDEX_SHA != $INDEX_SHA ]]; then
        echo "Index SHA changed, redownloading index..."
        rm /tmp/unstable-index.xml
        curl -s $INDEX_XZ_URL -o /tmp/unstable-index.xml.xz
        unxz /tmp/unstable-index.xml.xz
        INDEX_SHA=$NEW_INDEX_SHA
    elif [[ $NEW_INDEX_SHA = $INDEX_SHA ]]; then
        echo "Index SHA unchanged."
    else
        echo "Unknown error occured."
        rm /tmp/unstable-index.xml.xz /tmp/unstable-index.xml
        exit
    fi
}

i=0
# Look for the tag in the index
# FIXME: some packages like libreoffice do not output a eopkg file matching the tag
while [[ $(grep ${TAG} < /tmp/unstable-index.xml | wc -l) -lt 1 ]] ; do
    ((i=i+1))
    # Wait up to a minute (60 / (sleep) 5 = 12) before bailing
    if [[ $i == 12 ]]; then
        echo "${TAG} successfully built but hasn't been found in the index yet, please manually check."
        notify-send -u low "${TAG} successfully built but hasen't been found in the index yet, please manually check." -t 0
        paplay /usr/share/sounds/freedesktop/stereo/dialog-warning.oga
        rm /tmp/unstable-index.xml
        exit 1
    fi
    sleep 5
    # Download the new index
    echo "INDEX SHA: ${INDEX_SHA}"
    download_extract_index_if_changed
done

# Successfully built and indexed, we're happy bunnies.
echo "Successfully indexed into the repo!"
notify-send "${TAG} indexed into the repo!" -t 0
paplay /usr/share/sounds/freedesktop/stereo/complete.oga
rm /tmp/unstable-index.xml
