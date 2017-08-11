#!/bin/sh

# Adapted from Arch Linux script

if [ -d /sys/kernel/security/apparmor ]; then
    aa_profiles='/etc/apparmor.d/'
    aa_log='/var/log/apparmor.init.log'
    find "$aa_profiles" -maxdepth 1 -type f -exec /sbin/apparmor_parser -R {} \; 2>> "$aa_log"
   if [ -d /var/lib/snapd/apparmor/profiles ]; then
        aa_profiles="/var/lib/snapd/apparmor/profiles"
        find "$aa_profiles" -maxdepth 1 -type f -exec /sbin/apparmor_parser -R {} \; 2>> "$aa_log"
    fi
fi
