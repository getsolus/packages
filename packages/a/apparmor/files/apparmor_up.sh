#!/bin/sh

# Adapted from Arch Linux script

if [ -d /sys/kernel/security/apparmor ]; then
    aa_profiles='/etc/apparmor.d/'
    aa_log='/var/log/apparmor.init.log'
    find "$aa_profiles" -maxdepth 1 -type f -exec /sbin/apparmor_parser -r {} + 2>> "$aa_log"
fi
