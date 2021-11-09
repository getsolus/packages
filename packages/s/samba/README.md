# Solus Samba maintainer guidelines

This document is intended to serve as a knowledge base for current and future Solus Samba maintainers and to mitigate bus factor.


## The benefits of staying off the bleeding edge

In Solus, we don't generally track the newest Samba release branch.

Instead, we prefer to stay on the well tested [maintenance branch](https://wiki.samba.org/index.php/Samba_Release_Planning#Samba_Release_Planning_and_Supported_Release_Lifetime).  So if the newest release series is 4.11.x, we'll stay on the 4.10.x maintenance series until the latest release becomes 4.12.x, at which point we'll move to 4.11.x.

This puts us on a stable and mature code base for a feature (file-sharing) that should mostly stay "just works"/invisible to the end user.


## Bare bones build configuration

The Solus Samba build is intentionally quite bare-bones, with no support for Active Directory or Python out of the box.

This choice was made because Solus is targeted at home Desktop Users with the equivalent of workgroup file-sharing needs.

As an aside, Solus comes with a [custom Samba configuration](https://getsol.us/articles/software/samba/en/) which is intentionally kept as simple as possible.


## How to determine internal Samba dependency requirements for a given tagged release

The Solus Samba build relies on external build deps of certain Samba project libraries, which means that these external build deps need to be updated before attempting to update Samba proper.

In the Samba `package.yml` recipe, the line `!cmocka,!tdb,!talloc,!pytalloc-util,!tevent,!popt,!ldb,!pyldb-util` indicates which bundled/internal libraries need their version checked.  The `py*` packages are built as part of their respective C-language components (`talloc -> pytalloc-util`, `ldb -> pyldb-util`) when the respective builds have Python enabled.

To inspect the dependencies, first do a `git checkout $tag` in your up-to-date [upstream Samba git repository](https://gitlab.com/samba-team/samba) clone. 

Example:

```
git checkout master
git pull
git checkout samba-4.10.10
```

### Internal Samba dependencies (developed as part of Samba)

The shipped version for each of the bundled internal libraries is recorded at the top of each of their respective WAF `wscript` build files.

Checking the necessary versions might be done with the following bash snippet executed from the clone root:

```
for pkg in talloc tevent tdb ldb; do
    egrep -Hin '^VERSION =' "lib/${pkg}/wscript"
    eopkg info ${pkg} |grep Name |uniq
done
```

... which might yield output similar to:


```
ermo@rocinante:~/src/samba ⑂samba-4.10.10
$ for pkg in talloc tevent tdb ldb; do
>     egrep -Hin '^VERSION =' "lib/${pkg}/wscript"
>     eopkg info ${pkg} |grep Name |uniq
> done
lib/talloc/wscript:4:VERSION = '2.1.16'
Name                : talloc, version: 2.1.16, release: 9
lib/tevent/wscript:4:VERSION = '0.9.39'
Name                : tevent, version: 0.9.39, release: 10
lib/tdb/wscript:4:VERSION = '1.3.18'
Name                : tdb, version: 1.3.18, release: 13
lib/ldb/wscript:4:VERSION = '1.5.6'
Name                : ldb, version: 1.5.5, release: 11

```

In this example, ldb needs to be updated from 1.5.5 -> 1.5.6 in the Solus repo prior to building and landing Samba-4.10.10.

### 3rd Party Samba dependencies (only shipped as part of Samba for convenience)

The necessary `cmocka` and `popt` versions aren't listed in the respective wscript files, so the required versions will (sadly) only reveal themselves at build time if the versions are not recent enough.

Fortunately, both are mature pieces of software which means that new releases are rare.


## Worst case Samba rebuild stack:

Samba and its dependencies need to be rebuilt in a certain order.  For major version updates, the procedure typically involves rebuilding talloc, tevent, tdb and ldb before rebuilding Samba proper.

Within the same major version branch, the need to rebuild talloc/tevent/tdb/ldb is typically lower.

When doing major version updates, create a phab task with associated diff stack for review.

### talloc safety rebuilds (eopkg-deps rev talloc)

- ldb
- notmuch
- (samba)
- tevent
- cifs-utils 

### tevent safety rebuilds (eopkg-deps rev tevent)

- ldb
- (samba)

### tdb safety rebuilds (eopkg-deps rev tdb)

- ldb
- rhythmbox
- (samba)
- (tdb-utils is built as part of tdb)

### ldb safety rebuilds (eopkg-deps rev ldb)

- (samba)

### Packages that will need a safety rebuild if Samba exports ABI changes (eopkg-deps rev samba)

- ffmpeg
- gnome-control-center
- gvfs
- kio-extras
- python-pysmbc
- vlc

## Suggested Test Plan for each Samba rebuild

- Run `sudo testparm -v` and check for anomalies in the default config
- Run `sudo systemctl enable --now smb ; smbclient -N -L localhost` and check that the service runs and that it is possible to connect to the smb daemon
  - Look for `smbd` and ports 139 and 445 in `sudo ss -plantu |egrep '139|445|smbd'`
- Rebuild current `gvfs` and `kio-extras` (especially important if there were removals in abi_symbols)
  - Reboot and ensure that anonymous and authenticated user access works in the Dolphin (kio) and Nautilus (gvfs) file managers
- Rebuild `ffmpeg` and `vlc` (especially important if there were removals in abi_symbols)
  - Ensure that smb:// URI playback works in
    - `mpv` (used by GNOME MPV in Budgie and GNOME Shell)
    - `smplayer` (used by KDE)
    - `vlc` (used by MATE); note that vlc can be temperamental in this regard -- see T8538
