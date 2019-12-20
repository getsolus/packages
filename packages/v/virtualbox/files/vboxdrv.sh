#! /bin/sh
# Oracle VM VirtualBox
# Linux kernel module init script

#
# Copyright (C) 2006-2015 Oracle Corporation
#
# This file is part of VirtualBox Open Source Edition (OSE), as
# available from http://www.virtualbox.org. This file is free software;
# you can redistribute it and/or modify it under the terms of the GNU
# General Public License (GPL) as published by the Free Software
# Foundation, in version 2 as it comes in the "COPYING" file of the
# VirtualBox OSE distribution. VirtualBox OSE is distributed in the
# hope that it will be useful, but WITHOUT ANY WARRANTY of any kind.
#

# THIS IS A "MUCH SIMPLIFIED" VERSION OF THE ORIGINAL SCRIPT

PATH=/sbin:/bin:/usr/sbin:/usr/bin:$PATH
DEVICE=/dev/vboxdrv
LOG="/var/log/vbox-install.log"
MODPROBE=/sbin/modprobe
SCRIPTNAME=vboxdrv.sh

if $MODPROBE -c | grep -q '^allow_unsupported_modules  *0'; then
  MODPROBE="$MODPROBE --allow-unsupported-modules"
fi

begin_msg()
{
    test -n "${2}" && echo "${SCRIPTNAME}: ${1}."
    logger -t "${SCRIPTNAME}" "${1}."
}

succ_msg()
{
    logger -t "${SCRIPTNAME}" "${1}."
}

fail_msg()
{
    echo "${SCRIPTNAME}: failed: ${1}." >&2
    logger -t "${SCRIPTNAME}" "failed: ${1}."
}

failure()
{
    fail_msg "$1"
    exit 1
}

running()
{
    lsmod | grep -q "$1[^_-]"
}

start()
{
    begin_msg "Starting VirtualBox services" console
    if [ -d /proc/xen ]; then
        failure "Running VirtualBox in a Xen environment is not supported"
    fi
    if ! running vboxdrv; then
        if ! rm -f $DEVICE; then
            failure "Cannot remove $DEVICE"
        fi
        if ! $MODPROBE vboxdrv > /dev/null 2>&1; then
            failure "modprobe vboxdrv failed. Please use 'dmesg' to find out why"
        fi
        sleep .2
    fi
    # ensure the character special exists
    if [ ! -c $DEVICE ]; then
        MAJOR=`sed -n 's;\([0-9]\+\) vboxdrv$;\1;p' /proc/devices`
        if [ ! -z "$MAJOR" ]; then
            MINOR=0
        else
            MINOR=`sed -n 's;\([0-9]\+\) vboxdrv$;\1;p' /proc/misc`
            if [ ! -z "$MINOR" ]; then
                MAJOR=10
            fi
        fi
        if [ -z "$MAJOR" ]; then
            rmmod vboxdrv 2>/dev/null
            failure "Cannot locate the VirtualBox device"
        fi
        if ! mknod -m 0660 $DEVICE c $MAJOR $MINOR 2>/dev/null; then
            rmmod vboxdrv 2>/dev/null
            failure "Cannot create device $DEVICE with major $MAJOR and minor $MINOR"
        fi
    fi

    if ! $MODPROBE vboxnetflt > /dev/null 2>&1; then
        failure "modprobe vboxnetflt failed. Please use 'dmesg' to find out why"
    fi
    if ! $MODPROBE vboxnetadp > /dev/null 2>&1; then
        failure "modprobe vboxnetadp failed. Please use 'dmesg' to find out why"
    fi
    # Create the /dev/vboxusb directory if the host supports that method
    # of USB access.  The USB code checks for the existance of that path.
    if grep -q usb_device /proc/devices; then
        mkdir -p -m 0750 /dev/vboxusb 2>/dev/null
        chown root:vboxusers /dev/vboxusb 2>/dev/null
    fi

    succ_msg "VirtualBox services started"
}

stop()
{
    begin_msg "Stopping VirtualBox services" console

    if running vboxnetadp; then
        if ! rmmod vboxnetadp 2>/dev/null; then
            failure "Cannot unload module vboxnetadp"
        fi
    fi
    if running vboxdrv; then
        if running vboxnetflt; then
            if ! rmmod vboxnetflt 2>/dev/null; then
                failure "Cannot unload module vboxnetflt"
            fi
        fi
        if ! rmmod vboxdrv 2>/dev/null; then
            failure "Cannot unload module vboxdrv"
        fi
        if ! rm -f $DEVICE; then
            failure "Cannot unlink $DEVICE"
        fi
    fi
    succ_msg "VirtualBox services stopped"
}

dmnstatus()
{
    if running vboxdrv; then
        str="vboxdrv"
        if running vboxnetflt; then
            str="$str, vboxnetflt"
            if running vboxnetadp; then
                str="$str, vboxnetadp"
            fi
        fi
        echo "VirtualBox kernel modules ($str) are loaded."
    else
        echo "VirtualBox kernel module is not loaded."
    fi
}

case "$1" in
start)
    start
    ;;
stop)
    stop
    ;;
restart)
    stop && start
    ;;
force-reload)
    stop
    start
    ;;
status)
    dmnstatus
    ;;
*)
    echo "Usage: $0 {start|stop|restart|force-reload|status}"
    exit 1
esac

exit 0
