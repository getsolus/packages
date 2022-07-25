#!/bin/sh

# Requires notify-send.

# Script to determine whether a published tag has completed on the build server and gives you a notification whether it has completed or failed.
# If the unstable repo is found it will also notify when the package has been indexed into the repo.

TAG=$(.././common/Scripts/gettag.py package.yml)

# Check it's actually been published first.
if [[ ! $(curl -s https://build.getsol.us | grep "${TAG}") ]] ; then
    echo "${TAG} not found on build queue, has it been published?"
    exit
fi

# Get the latest build-id for the $TAG
BUILDID=$(curl -s https://build.getsol.us | grep -B 1 "${TAG}" | grep -o '[0-9]*' | sort -nr | head -1)
echo "Build ID: ${BUILDID} | Tag: ${TAG}"

# Look for build-ok from the build id
while [[ ! $(curl -s https://build.getsol.us | grep -A 4 ${BUILDID} | grep build-ok) ]] ; do

    # Don't DoS the server
    sleep 20

    # Check if the build has failed
    if [[ $(curl -s https://build.getsol.us | grep -A 4 ${BUILDID} | grep build-failed) ]] ; then
        notify-send -u critical "${TAG} failed on the build server!" -t 0
        paplay /usr/share/sounds/freedesktop/stereo/suspend-error.oga
        exit 1
    fi
done

# Only check if it's been indexed if the unstable repo exists
# FIXME: the unstable repo can be called anything, how to make less hardcodey?
UNSTABLE_FILE=/var/lib/eopkg/index/Unstable/eopkg-index.xml
if [[ -f "$UNSTABLE_FILE" ]]; then

    echo "${TAG} successfully built, waiting for it to be indexed..."
    notify-send "${TAG} successfully built! Input password to get indexing check" -t 0
    paplay /usr/share/sounds/freedesktop/stereo/message.oga

    echo "> Updating unstable to check..."
    while [[ $(grep ${TAG} < $UNSTABLE_FILE | wc -l) -lt 1 ]] ; do
        sudo eopkg ur
        i=0
        let "i+=1"
        # Wait for one minute
        if [[ $i == 12 ]]; then
            echo "${TAG} Successfully built but hasen't been found in the index yet, please manually check."
            notify-send -u low "${TAG} successfully built but hasen't been found in the index yet, please manually check." -t 0
            paplay /usr/share/sounds/freedesktop/stereo/dialog-warning.oga
            exit 1
        fi
        sleep 5
    done
    # Send notification and play sound for indexing check
    echo "${TAG} indexed into the repo!"
    notify-send "${TAG} indexed into the repo!" -t 0
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga
else
    # Send notification and play sound for no indexing check
    echo "Unstable repo not found, skipping indexing check."
    echo "${TAG} finished building!"
    notify-send "${TAG} finished building!" -t 0
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga
fi
