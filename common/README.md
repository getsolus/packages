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
