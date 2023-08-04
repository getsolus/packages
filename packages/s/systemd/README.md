# systemd secure boot support in git submodule

## Cloning

When cloning this repo, please use `git clone --recurse-submodules <URI>`.

Without this, the solus secure boot certificate will not be included in the build manifest after a successful build.

## Updating

If you already have a clone of the systemd repo but have not yet added the git submodule, you can do so with:

`git submodule update --init --recursive`

This will initialise and fetch an up-to-date version of the submodule into your working copy.
