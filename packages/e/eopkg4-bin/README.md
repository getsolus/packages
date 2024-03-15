# eopkg4-bin
This packages a compiled binary of eopkg, including all its dependencies (except glibc). The resulting binary can be run even with no python installed at all, though you probably don't want to. The point is that eopkg, when compiled this way, is much more resilient to system python upgrades.

## Caveats
1. This is a very new packaging effort, building a binary version of a relatively untested python3 version of eopkg. It *probably* won't break your system, but it *definitely could*. **Do not use this if you don't know what you're doing**.
2. This package patches `eopkg4` to use a separate files database from your system's existing python2-based eopkg. It might be necessary to run `eopkg rdb` occasionally (on both `eopkg` and `eopkg4-bin`) to keep things in sync.
3. The first time you use `eopkg4-bin`, the package database pickle cache will be updated. If you then try to run `eopkg` (the standard python2 version), you will get an error. To resolve this, run `eopkg update-repo --force`. This will (forcibly) update your eopkg package database, regenerating the aforementioned cache.
4. There's an exception in the PackageKit backend when it starts, but it seems to function after that. I've tried installing and removing packages so far. This requires further investigation.
5. ***Do not use this if you don't know what you're doing.***

## Steps for testing
1. Report your test results in the [eopkg4-bin testing issue](https://github.com/getsolus/packages/issues/1316).

## Validating that PackageKit is using the correct backend
1. Run `sudo /usr/lib/packagekit/packagekitd -v`. This will start the packagekit daemon and show you all of its logs.
2. If the packagekitd log contains this line, you are using the eopkg3 (Python 2) backend: `using spawn filename /usr/share/PackageKit/helpers/eopkg/eopkgBackend.py`. Note the extension `.py`.
3. If the packagekitd log contains this line, you are using the nuitka-compiled eopkg4 (Python 3) backend: `using spawn filename /usr/share/PackageKit/helpers/eopkg/eopkgBackend.bin`. Note the extension `.bin`.
