#!/usr/bin/env bash

# Script to determine whether a published tag has completed on the build server and gives you a notification whether it has completed or failed.
# Additionally, if a package successfully builds it will then check if it gets successfully indexed into the repo.

# Check requirements before starting
REQUIREMENTS="curl unxz notify-send paplay"
for i in $REQUIREMENTS; do
    if ! which $i &> /dev/null; then
        echo "Missing requirement: $i. Install it to continue."
        exit 1
    fi
done

if [[ ! -z "${DISABLE_BUILD_SUCCESS_NOTIFY}" ]]; then
    # For rebuild-template-script.sh
    echo "Notification and sound ping for build success disabled due to DISABLE_BUILD_SUCCESS_NOTIFY being set."
fi

TAG=$(.././common/Scripts/gettag.py package.yml)
BUILDSERVER_URL="https://build.getsol.us"
BUILDPAGE="/tmp/buildpage.html"

# Download the page
curl -s $BUILDSERVER_URL -o $BUILDPAGE

# Check it's actually been published first.
if [[ ! $(grep "${TAG}" "${BUILDPAGE}" ) ]] ; then
    echo "${TAG} not found on build queue, has it been published?"
    exit 1
fi

# Get the latest build-id for the $TAG
BUILDID=$(grep -B 1 "${TAG}" "${BUILDPAGE}" | grep -o '[0-9]*' | sort -nr | head -1)
echo "Build ID: ${BUILDID} | Tag: ${TAG}"

# Look for build-ok from the build id
while [[ ! $(grep -A 4 "${BUILDID}" "${BUILDPAGE}" | grep ">ok<") ]] ; do

    # Don't DoS the server
    sleep 20

    # Download new build page if-modified-since (-z)
    curl -s -z $BUILDPAGE $BUILDSERVER_URL -o $BUILDPAGE

    # Check if the build has failed
    if [[ $(grep -A 4 "${BUILDID}" "${BUILDPAGE}" | grep ">failed<") ]] ; then
        echo "Failed on the build server!"
        notify-send -u critical "${TAG} failed on the build server!" -t 0
        paplay /usr/share/sounds/freedesktop/stereo/suspend-error.oga
        exit 1
    fi
done

echo "Build succeeded on the buildserver! Waiting for it to be indexed..."
rm ${BUILDPAGE}

### Now that it's built ensure we find it indexed into the repo.

# Setup for index check
INDEX_SHA_URL="https://cdn.getsol.us/repo/unstable/eopkg-index.xml.xz.sha1sum"
INDEX_XZ_URL="https://cdn.getsol.us/repo/unstable/eopkg-index.xml.xz"
INDEX_SHA=$(curl -s $INDEX_SHA_URL)
curl -s $INDEX_XZ_URL -o /tmp/unstable-index.xml.xz
unxz /tmp/unstable-index.xml.xz

# Downloads and extracts the new index if the sha sum has changed.
update_index_if_changed() {
    NEW_INDEX_SHA=$(curl -s $INDEX_SHA_URL)

    # New sha, grab the new index
    if [[ $NEW_INDEX_SHA != $INDEX_SHA ]]; then
        INDEX_SHA=$NEW_INDEX_SHA
        echo "index sha: ${INDEX_SHA}"
        rm /tmp/unstable-index.xml
        curl -s $INDEX_XZ_URL -o /tmp/unstable-index.xml.xz
        unxz /tmp/unstable-index.xml.xz
    # Same sha, do nothing
    elif [[ $NEW_INDEX_SHA = $INDEX_SHA ]]; then
        echo "index sha: ${INDEX_SHA}"
    else
        echo "Unknown error occured."
        rm /tmp/unstable-index.xml.xz /tmp/unstable-index.xml
        exit 1
    fi
}

# Look for the tag in the index
# FIXME: some packages like libreoffice do not output a eopkg file matching the tag
while [[ $(grep ${TAG} < /tmp/unstable-index.xml | wc -l) -lt 1 ]] ; do
    var=$((var+1))
    # Wait up to 1m:30s (90 / (sleep) 5 = 18) before bailing
    if [[ $var == 18 ]]; then
        echo "Successfully built but hasn't been found in the index yet, please manually check."
        notify-send -u low "${TAG} successfully built but hasen't been found in the index yet, please manually check." -t 0
        paplay /usr/share/sounds/freedesktop/stereo/dialog-warning.oga
        rm /tmp/unstable-index.xml
        exit 1
    fi
    sleep 5
    # Check for new index
    update_index_if_changed
done

# Successfully built and indexed, we're happy bunnies.
echo "Successfully indexed into the repo!"
if [[ -z "${DISABLE_BUILD_SUCCESS_NOTIFY}" ]]; then
    notify-send "${TAG} indexed into the repo!" -t 0
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga
fi
rm /tmp/unstable-index.xml
