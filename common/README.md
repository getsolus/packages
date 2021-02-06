# common 

See [this page](https://getsol.us/articles/packaging/building-a-package/en/#setting-up-common) for setup documentation.

## Repositories

### Cloning

To clone all repositories indicated in our `packages` file, run the below mentioned command. Please note that this list is not comprehensive and members of the Solus Team are required to run separate tooling to ensure this `packages` file is up-to-date (to include new files or remove deprecated ones):

```
make clone
```

### Updating

To update all cloned repositories, run the following:

```
make pull
```

### Building

To build a package, first ensure solbuild is set up and the adequate symlinks are set up. This can be done by following our Building a Package documentation on the Help Center, linked at the top of this document.

Go into the directory of the package you wish to build and type:

```
make
```

### Publish

Submission is only possible for maintainers. As a maintainer you may freely push to your package(s) and initiate builds for them, which will be pushed to the unstable repository. You can watch builds at the [Solus Package Build Status Page](https://build.getsol.us/)

If you're submitting a `package.yml` build, ensure you also commit the `pspec_$ARCH.xml`
file, as builds are created from git tags.

```
cd $somepkg
make publish
```

## solbuild

Install `solbuild` from the main repository. **All** builds are performed in the unstable repository, so `unstable-x86_64` is the default build profile.

Install `solbuild-config-unstable` to lock builds to the unstable repository.

See `man solbuild` for further details.

## Notes on `yabi`

Says Bryan:

Alright, there seems to be some miscommunication about what yabi can and can't do and I'm getting a little annoyed at having to explain this over an over in different places.

1. `yabi` can and will mark libraries as missing if it cannot find them on your system.
2. `yabi` can and will mark libraries as missing if it cannot find matches for symbols inside the library. I haven't had a chance to make the errors more verbose, so you'll have to use your judgment.
3. It's OK to submit patches with UNKNOWN in abi_used_libs or abi_used_symbols. If you are updating a package and it's not part of a local stack upgrade, you probably have everything installed on your machine and it will work fine.
4. `yabi` does not run inside the chroot so it won't see files from packages getting installed from your local repo. This won't be getting fixed until `ypkg3` handles ABI stuff inside the chroot. And that's perfectly fine as the point of yabi is to make sure we have the new abi_used_symbols files. If a symbol has an unknown library, it's still at least recorded and a `grep` will find it and any additional information over what `abireport` can tell us, which is still an improvement.
5. I intentionally made it so that `yabi` would update the ABI reports even if libraries are marked as missing. This is to work around (4). If you think it's a bug, please check against (1) and (2).
6. Please file bugs against `yabi` on Phab -- `abi-wizard` issues should NOT be used for `yabi`.
