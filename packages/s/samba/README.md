# Solus Samba maintainer guidelines

This document is intended to serve as a knowledge base for current and future Solus Samba maintainers and to mitigate bus factor.


## The benefits of staying off the bleeding edge

In Solus, we don't generally track the newest Samba release branch.

Instead, we prefer to stay on the well tested [maintenance branch](https://wiki.samba.org/index.php/Samba_Release_Planning#Samba_Release_Planning_and_Supported_Release_Lifetime).  So if the newest release series is 4.11.x, we'll stay on the 4.10.x maintenance series until the latest release becomes 4.12.x, at which point we'll move to 4.11.x.

This puts us on a stable and mature code base for a feature (file-sharing) that should mostly stay "just works"/invisible to the end user.


## Bare bones build configuration

The Solus Samba build is intentionally quite bare-bones, with no support for Active Directory or Python out of the box.

This choice was made because Solus is targeted at home Desktop Users with the equivalent of workgroup file-sharing needs.

As an aside, Solus comes with a [custom Samba configuration](https://help.getsol.us/docs/user/software/networking/samba) which is intentionally kept as simple as possible.


## How to determine internal Samba dependency requirements for a given tagged release

The Solus Samba build relies on external build deps of certain Samba project libraries, which means that these external build deps need to be updated before attempting to update Samba proper.

In the Samba `package.yml` recipe, the line `!cmocka,!tdb,!talloc,!pytalloc-util,!tevent,!popt,!ldb,!pyldb-util` indicates which bundled/internal libraries need their version checked.  The `py*` packages are built as part of their respective C-language components (`talloc -> pytalloc-util`, `ldb -> pyldb-util`) when the respective builds have Python enabled.

To inspect the dependencies, first do a `git checkout $tag` in your up-to-date [upstream Samba git repository](https://gitlab.com/samba-team/samba) clone. 

Example:

```
git checkout master
git pull
git checkout samba-4.19.6
```


### Internal Samba dependencies (developed as part of Samba)

The shipped version for each of the bundled internal libraries is recorded at the top of each of their respective WAF `wscript` build files.

Checking the necessary versions might be done with the following bash snippet executed from the clone root:

```
for pkg in talloc tevent tdb; do
    grep -EHin '^VERSION =' "lib/${pkg}/wscript"
    eopkg info ${pkg} |grep Name |uniq
done
```

... which might yield output similar to:


```
ermo@solbox:~/repos/samba [samba-4.19.6]
$ for pkg in talloc tdb tevent; do
    grep -EHin '^VERSION =' "lib/${pkg}/wscript"
    eopkg info ${pkg} |grep Name |uniq
done
lib/talloc/wscript:4:VERSION = '2.4.1'
Name                : talloc, version: 2.3.4, release: 16
Name                : talloc, version: 2.4.1, release: 17
lib/tdb/wscript:4:VERSION = '1.4.9'
Name                : tdb, version: 1.4.7, release: 24
lib/tevent/wscript:4:VERSION = '0.15.0'
Name                : tevent, version: 0.13.0, release: 18
```

In this example (samba 4.17.12 -> 4.19.6):

- talloc needs to be updated from 2.3.4 -> 2.4.1
- tevent needs to be updated from 0.13.0 -> 0.15.0
- tdb needs to be updated from 1.4.7 -> 1.4.9

in the Solus repo prior to building and landing Samba-4.19.6.


### 3rd Party Samba dependencies (only shipped as part of Samba for convenience)

The necessary `cmocka` and `popt` versions aren't listed in the respective wscript files, so the required versions will (sadly) only reveal themselves at build time if the versions are not recent enough.

Fortunately, both are mature pieces of software which means that new releases are rare.


## Worst case Samba rebuild stack:

Samba and its dependencies need to be rebuilt in a certain order.  For major version updates, the procedure typically involves rebuilding talloc, tevent, and tdb before rebuilding Samba proper.

Within the same major version branch, the need to rebuild talloc/tevent/tdb is typically lower.

When doing major version updates, create a GH PR with commits ordered per the below list for review and easy pushing+building.


### Tiers and rebuild order

```
$ autobuild query -t src:packages/ samba tdb tevent talloc
Build order:
 Tier 1: talloc tdb
 Tier 2: cifs-utils notmuch tevent
 Tier 3: samba
 Tier 4: *acccheck ffmpeg python-pysmbc
 Tier 5: budgie-control-center gvfs kio-extras mpd *nautilus-share *nemo-extensions rhythmbox vlc
 Tier 6: gnome-control-center
```

A few of the above packages only have samba as a rundep (marked with *), so can be ignored for rebuilds.


### Related packages that should be checked for updates on a regular basis

- [cifs-utils](https://www.samba.org/ftp/linux-cifs/cifs-utils/)
- [python-pysmbc](https://files.pythonhosted.org/packages/source/p/pysmbc/)
- [wsdd](https://github.com/christgau/wsdd/tags)


## Suggested Test Plan for each Samba rebuild

- Run `sudo testparm -v` and check for anomalies in the default config
- Run `sudo systemctl enable --now smb ; smbclient -N -L 127.0.0.1` and check that the service runs and that it is possible to connect to the smb daemon
  - Look for `smbd` and ports 139 and 445 in `sudo ss -plantu |grep -E '139|445|smbd'`
- Reboot and ensure that anonymous and authenticated user access works in the Dolphin (kio) and Nautilus (gvfs) file managers
- Ensure that smb:// URI playback works in:
  - `celluloid` (used by Budgie and GNOME)
  - `haruna` (used by KDE)
  - `mpv` (unauthenticated access will work fine, but authenticated access will not)
  - `parole` (used by XFCE)
  - `vlc` -- note that vlc can be temperamental in this regard -- see T8538
