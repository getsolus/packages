# eopkg4-bin
This packages a compiled binary of eopkg, including all its dependencies (except glibc). The resulting binary can be run even with no python installed at all, though you probably don't want to. The point is that eopkg, when compiled this way, is much more resilient to system python upgrades.

## Caveats
1. This is a very new packaging effort, building a binary version of a relatively untested python3 version of eopkg. It *probably* won't break your system, but it *definitely could*. **Do not use this if you don't know what you're doing**.
2. This package patches `eopkg4` to use a separate files database from your system's existing python2-based eopkg. It might be necessary to run `eopkg rdb` occasionally (on both `eopkg` and `eopkg4-bin`) to keep things in sync.
3. The first time you use `eopkg4-bin`, the package database pickle cache will be updated. If you then try to run `eopkg` (the standard python2 version), you will get an error. To resolve this, run `eopkg update-repo --force`. This will (forcibly) update your eopkg package database, regenerating the aforementioned cache.
4. There's an exception in the PackageKit backend when it starts, but it seems to function after that. I've tried installing and removing packages so far. This requires further investigation.
5. ***Do not use this if you don't know what you're doing.***

## Steps for testing
1. Check out the `eopkg4-bin` branch of this repository (`getsolus/packages`).
2. Test PackageKit first.
	1. Go to the packagekit package (`gotopkg packagekit`).
	2. Build packagekit and copy it to your local repo (`go-task localcp`
	3. Install the new packagekit package *before* you do anything with eopkg4-bin
	4. Test some PackageKit operations (with pkcon, Discover, or Gnome Software) and report your test results in the [eopkg4-bin testing issue](https://github.com/getsolus/packages/issues/1316). The PackageKit package in this PR is patched to work with the existing eopkg3 backend until eopkg4-bin is installed, and switch to the compiled backend at runtime. We need to validate that this works before landing the PR.
5. Test eopkg4-bin.
	1. Go to the eopkg4-bin package (`gotopkg eopkg4-bin`)
	2. Build the package using your local repository (`go-task local`)
	3. Install the resulting `.eopkg`
	4. The compiled eopkg binary can now be run as `eopkg4-bin`, and PackageKit should switch automatically to using the new compiled backend.
5. Make yourself familiar with how to tell which backend is in use by PackageKit. Switch back and forth a couple times to make sure it's working. Note caveat 3 as you do this.
6. Report your test results in the [eopkg4-bin testing issue](https://github.com/getsolus/packages/issues/1316).
7. Report any issues with the package itself (building, etc.) [on the draft PR](https://github.com/getsolus/packages/pull/1305).

## Validating that PackageKit is actually switching backends
1. Once you've installed the PRed PackageKit package, but without eopkg4-bin installed, run `sudo /usr/lib/packagekit/packagekitd -v`. This will start the packagekit daemon and show you all of its logs. 
2. Check the packagekitd logs for an instance of this line: `using spawn filename /usr/share/PackageKit/helpers/eopkg/eopkgBackend.py`. The extension `.py` indicates that PackageKit is accessing the Python2 backend.
3. Install `eopkg4-bin` per above testing instructions.
4. Run `sudo /usr/lib/packagekit/packagekitd -v` again. 
5. Check the log for an instance of this line: `using spawn filename /usr/share/PackageKit/helpers/eopkg/eopkgBackend.bin`. The extension `.bin` indicates that PackageKit is using the compiled python3 backend.