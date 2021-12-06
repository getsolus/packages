#!/bin/sh

# Requires notify-send.

# Script to determine whether a published tag has completed on the build server and gives you a notification whether it has completed or failed.

TAG=$(.././common/Scripts/gettag.py package.yml)

# Check it's actually been published first.
if [[ ! $(curl -s https://build.getsol.us | grep "${TAG}") ]] ; then
    echo "${TAG} not found on build queue, has it been published?"
    exit
fi

# Look for build-ok from the tag
while [[ ! $(curl -s https://build.getsol.us | grep -A 3 ${TAG} | grep build-ok) ]] ; do

    # Don't DoS the server
    sleep 20

    # Check if the build has failed
    # FIXME: republish case, the tag doesn't change. Does buildid change? Otherwise, date will have to used somehow.
    if [[ $(curl -s https://build.getsol.us | grep -A 3 "${TAG}" | grep build-failed) ]] ; then
        notify-send -u critical "${TAG} failed on the build server!" -t 0
        paplay /usr/share/sounds/freedesktop/stereo/suspend-error.oga
    fi
done

# Send notification and play sound
notify-send "${TAG} finished building!" -t 0
paplay /usr/share/sounds/freedesktop/stereo/complete.oga
