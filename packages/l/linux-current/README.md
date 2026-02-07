## How to update and build a Solus kernel

For minor version updates (Z in X.Y.Z), the process looks roughly like this:

- Run `grep http package.yml` in the `l/linux-current` recipe dir
- Run `yupdate <the new version> <the URI from above with the new version>`
- go-task
- If the build finishes, you're done updating the kernel itself, and can move on to consulting REBUILDS.md
- However, if ^ gets stuck asking for new modules, do the following:
  - Run CTRL+C and stop the build
  - Run `sudo solbuild chroot` and go into the chroot
  - Run `cd YPKG/root/linux-current/build/linux-<the version>`
  - In the root of the chroot kernel build dir, run `make oldconfig` then answer the questions.
    Typically, you will want to select `m` for new drivers.
    If you need to make bigger changes, you can run `make menuconfig` afterwards.
  - When you are happy, leave the terminal with the solbuild chroot open
  - Then, open a new terminal and navigate into the `l/linux-current/` recipe directory
  - Run `cp -v /var/cache/solbuild/unstable-x86_64/linux-current/union/home/build/YPKG/root/linux-current/build/linux-<the version>/.config files/config`
  - In the `l/linux-current directory`, run `git diff .` to check that the changes to the kernel build dir `.config` made it over to `files/config`
  - If everything looks ok, you can go back to the soldbuild terminal window and exit it
  - With the kernel config and version now updated, run `go-task build` and hopefully watch your kernel build
  - Once the build is done, add all the changes in a commit in a <yournick>/linux-current-<version>-update branch
  - ... and then proceed to bump/update and (re)build the recipes in REBUILDS.md and commit each to your branch.

The above approach can also work for major (Y in X.Y.Z) updates, but there's a higher likelihood of patches needing rebasing.
