# Solus Samba maintainer guidelines

This document is intended to serve as a knowledge base for current and future Solus Samba maintainers and to mitigate bus factor.

## The benefits of staying off the bleeding edge

In Solus, we don't generally move to the newest Samba release branch.  Instead, we prefer to stay on the well tested [maintenance branch](https://wiki.samba.org/index.php/Samba_Release_Planning#Samba_Release_Planning_and_Supported_Release_Lifetime).  So if the newest release series is 4.11.x, we'll stay on the 4.10.x maintenance series until the latest release becomes 4.12.x, at which point we'll move to 4.11.x.

This puts us on a stable and mature code base for a feature (file-sharing) that should mostly stay "just works"/invisible to the end user.

### Bare bones build configuration

The Solus Samba build is intentionally quite bare-bones, with no support for Active Directory or Python out of the box.  This is because Solus is targeted at home Desktop Users with the equivalent of workgroup file-sharing needs.

As an aside, Solus comes with a [custom Samba configuration](https://getsol.us/articles/software/samba/en/) which is intentionally kept as simple as possible.

## How to determine internal Samba dependency requirements for a given tagged release

The Solus Samba build relies on external build deps of certain Samba project libraries, which
means that these external build deps need to be updated before attempting to update Samba proper.

In your [vanilla samba clone](https://gitlab.com/samba-team/samba), do a `git checkout $tag`

Example:

```
git pull
git checkout samba-4.10.10
```

Then, look at the versions of the deps listed below:

- talloc:
-- look in lib/talloc/wscript
- tevent:
-- look in lib/tevent/wscript
- tdb:
-- look in lib/tdb/wscript
- ldb:
-- look in lib/ldb/wscript

This might be done with the following bash snippet executed from the clone root:

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

In this example, ldb needs to be updated from 1.5.5 -> 1.5.6 in the Solus repo.


## Worst case Samba rebuild stack:

Samba and its deps need to be rebuilt in a certain order. For major version updates, the procedure typically involves rebuilding talloc, tevent, tdb and ldb before rebuilding Samba
proper.

Within the same major version branch, the need to rebuild talloc/tevent/tdb/ldb is typically lower.

When doing major version updates, create a phab task with associated diff stacks for review.

### talloc safety rebuilds (eopkg-deps rev talloc)

- ldb
- notmuch
- (samba)
- tevent

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

- gnome-control-center
- gvfs
- kio-extras
- kodi (this takes around 1 hour on my system)
- kodi-devel (not listed by `eopkg-deps rev samba`, but still necessary)
- mpd
- mpv (mpv-libs is built as part of mpv)
- python-pysmbc
- vlc
