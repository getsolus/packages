#!/usr/bin/env bash

# Script to determine whether a published tag has completed on the build server and gives you a notification whether it has completed or failed.
# Additionally, if a package successfully builds it will then check if it gets successfully indexed into the repo.

# Check requirements before starting
REQUIREMENTS="curl unxz notify-send paplay jq"
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

if [ -f "package.yml" ]; then
    # Read the file from the latest commit in directory. Not from any potential unstaged changes
    SPECFILEREF=$(git show $(git rev-list -1 HEAD .):./package.yml > /tmp/tmp.yml)
    TAG=$($(git rev-parse --show-toplevel)/common/Scripts/gettag.py /tmp/tmp.yml)
    rm /tmp/tmp.yml
elif [ -f "pspec.xml" ]; then
    # Read the file from the latest commit in directory. Not from any potential unstaged changes
    SPECFILEREF=$(git show $(git rev-list -1 HEAD .):./pspec.xml > /tmp/tmp.xml)
    TAG=$($(git rev-parse --show-toplevel)/common/Scripts/gettag.py /tmp/tmp.xml)
    rm /tmp/tmp.xml
else
    echo "No valid package.yml or pspec.xml file found"
    exit 1
fi

BUILDSERVER_JSON_URL="https://build.getsol.us/builds.json"
JSONPAGE="/tmp/builds.json"

# Download the page
curl -sSL $BUILDSERVER_JSON_URL -o $JSONPAGE

# Check it's actually been published first.
if [[ ! $(jq '.[] | select(.tag == $ARGS.positional[0])' "${JSONPAGE}" --args "${TAG}") ]] ; then
    echo "${TAG} not found on build queue, has it been published?"
    exit 1
fi

# Get the latest build-id for the $TAG
BUILDID=$(jq '.[] | select(.tag == $ARGS.positional[0]) | .id' "${JSONPAGE}" --args "${TAG}" | grep -o '[0-9]*' | sort -nr | head -1)
echo "Build ID: ${BUILDID} | Tag: ${TAG}"

# Look for build-ok from the build id
while [[ ! $(jq '.[] | select(.tag == $ARGS.positional[0]) | .status' "${JSONPAGE}" --args "${TAG}" | grep "OK") ]]; do

    # Don't DoS the server
    sleep 20

    # Download new build page if-modified-since (-z)
    curl -sSL -z $JSONPAGE $BUILDSERVER_JSON_URL -o $JSONPAGE

    # Check if the build has failed
    if [[ $(jq '.[] | select(.tag == $ARGS.positional[0]) | .status' "${JSONPAGE}" --args "${TAG}" | grep "FAILED") ]] ; then
        echo "Failed on the build server!"
        notify-send -u critical "${TAG} failed on the build server!" -t 0
        paplay /usr/share/sounds/freedesktop/stereo/suspend-error.oga
        exit 1
    fi
done

echo "Build succeeded on the buildserver! Waiting for it to be indexed..."
if [ -f "${JSONPAGE}" ]; then rm ${JSONPAGE}; fi

### Now that it's built ensure we find it indexed into the repo.

# Setup for index check
INDEX_SHA_URL="https://cdn.getsol.us/repo/unstable/eopkg-index.xml.xz.sha1sum"
INDEX_XZ_URL="https://cdn.getsol.us/repo/unstable/eopkg-index.xml.xz"
INDEX_SHA=$(curl -s $INDEX_SHA_URL)
INDEX_XML="/tmp/unstable-index.xml"
curl -s $INDEX_XZ_URL -o ${INDEX_XML}.xz
unxz ${INDEX_XML}.xz -f

# Downloads and extracts the new index if the sha sum has changed.
update_index_if_changed() {
    NEW_INDEX_SHA=$(curl -s $INDEX_SHA_URL)

    # New sha, grab the new index
    if [[ $NEW_INDEX_SHA != $INDEX_SHA ]]; then
        INDEX_SHA=$NEW_INDEX_SHA
        echo "index sha: ${INDEX_SHA}"
        rm ${INDEX_XML}
        curl -s $INDEX_XZ_URL -o ${INDEX_XML}.xz
        unxz ${INDEX_XML}.xz -f
    # Same sha, do nothing
    elif [[ $NEW_INDEX_SHA = $INDEX_SHA ]]; then
        echo "index sha: ${INDEX_SHA}"
    else
        echo "Unknown error occured."
        if [ -f "${INDEX_XML}" ]; then rm ${INDEX_XML}; fi
        exit 1
    fi
}

# Look for the tag in the index
# FIXME: some packages like libreoffice do not output a eopkg file matching the tag
while [[ $(grep ${TAG} < ${INDEX_XML} | wc -l) -lt 1 ]] ; do
    var=$((var+1))
    # Wait up to 1m:30s (90 / (sleep) 5 = 18) before bailing
    if [[ $var == 18 ]]; then
        echo "Successfully built but hasn't been found in the index yet, please manually check."
        notify-send -u low "${TAG} successfully built but hasen't been found in the index yet, please manually check." -t 0
        paplay /usr/share/sounds/freedesktop/stereo/dialog-warning.oga
        if [ -f "${INDEX_XML}" ]; then rm ${INDEX_XML}; fi
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

if [ -f "${INDEX_XML}" ]; then rm ${INDEX_XML}; fi
