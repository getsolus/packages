Boot process
=============

Our kernels should take the form::

    /boot/vmlinuz-$VERSION-$RELEASE-$TYPE
    /boot/config-$VERSION-$RELEASE-$TYPE
    /boot/initrd.img-$VERSION-RELEASE-$TYPE
    /vmlinuz -> boot/vmlinuz-$VERSION-$RELEASE-$TYPE
    /initrd.img -> boot/initrd.img-$VERSION-$RELEASE-$TYPE

Dracut Changes
==============

Remove handling from dracut, and put this in *each* kernel modules
post-install.

On post-install, kernel should::

    /sbin/depmod $VERSION-$RELEASE-$TYPE
    dracut --kver $VERSION-$RELEASE-$TYPE -f blahblah..

Packaging changes
=================

Split kernel-libc-devel into it's own package, simply providing::

    /usr/include/*

This can be achieved with a simple package.yml, and *must* replace
the old package, which is to be removed from "kernel" source package.

Advise::

    linux-libc-devel
    # This is what it is, dev for klibc stuff

Or::

    linux-devel
    # Prettier, not quite accurate.


Changes to kernel package
=========================

The current "kernel" package will need to be removed. We'll create a
new package, with the "linux-" specifier, branched by MAJOR.MINOR::

    linux-4.1
    linux-4.1-headers
    linux-4.1-modules

    linux-4.3
    linux-4.3-headers
    linux-4.3-modules

    # future
    linux-4.4
    linux-4.4-headers
    linux-4.4-modules

Meta-packages
=============

In addition to the distinct branch policy, we'd maintain two meta-packages
to control upgrade and build flow

    *linux-lts*:

        Depend on latest LTS kernel (linux-4.1)

    *linux-lts-modules*:

        Depend on latest LTS modules (linux-4.1-modules)

    *linux-lts-headers*:

        Depend on latest LTS headers (linux-4.1-headers)

    *linux-mainline*:
        Depends on latest **stable** mainline kernel (linux-4.3)

    *linux-mainline-modules*:

        Depend on latest **stable** mainline kernel modules (linux-4.3-modules)

    *linux-mainline-headers*:

        Depend on latest **stable** mainline kernel headers (linux-4.3-headers)


Replacements
============

To facilitate the upgrade process, we'll use Replaces/Obsoletes to swap users
from the legacy "kernel*" packages to the new LTS branch::

    kernel         -> linux-lts
    kernel-modules -> linux-lts-modules
    kernel-headers -> linux-lts-headers

UEFI considerations:
======================

Each kernel post-installs its own namespaced kernel::

    /boot/efi/com.solus-project.$VERSION-$RELEASE-$TYPE.kernel
    /boot/efi/com.solus-project.$VERSION-$RELEASE-$TYPE.initrd

Matching /boot/efi/loader/entries/com.solus-project.$VERSION.$RELEASE-$TYPE::

    title Solus $VERSION-$RELEASE
    linux /com.solus-project.$VERSION-$RELEASE-$TYPE.kernel
    initrd /com.solus-project.$VERSION-$RELEASE-$TYPE.initrd
    options root=$(THEIR_ROOT_UUID) $(DEFAULT_OPTIONS)


Post install
============

Upon installing or updating a kernel set, changes then need to be made
on the filesystem to control the new default kernel to update to. The
default kernel is decided by matching the $TYPE, i.e. if the user is
running an LTS kernel (the default) then the new default will be the
highest release number of this kernel type. As such, if they are using
MAINLINE, then the highest release number in mainline is chosen.

All
'''

The links `/vmlinuz` and `/initrd.img` are updated to point to the new
default kernel and initrd within `/boot`.

GRUB/BIOS
'''''''''

`update-grub` is run after the modules and vmlinuz are both in place.

UEFI (goofiboot)
''''''''''''''''

A goofiboot loader configuration should be automatically written to the
ESP at `/boot/efi/loader/entries/com.solus-project.$VERSION-$RELEASE-$TYPE`

The `/boot/efi/loader/loader.conf` file is automatically updated to point to the correct
loader entry::

    timeout 4
    default com.solus-project.$VERSION-$RELEASE-$TYPE

Possibility
===========

Create a `linux-common` package in the legacy format to handle both the
depmod aspect, and `dracut` generation for all the kernel packages, which
would enable all kernel packages to be in the newer `package.yml` format
and built entirely with YPKG.
