Getting setup
------------

    git clone https://dev.getsol.us:2222/source/common.git
    ln -sv common/Makefile.common .
    ln -sv common/Makefile.toplevel Makefile
    ln -sv common/Makefile.iso .

Cloning all repositories
---------------------

    # This may take some time.
    make clone

Updating all repositories
-----------------------

    # This may take some time.
    make pull

Building a package
----------------

    # Ensure solbuild is setup..
    cd $somepkg
    make

Submitting a build
-----------------
Submission is only possible for maintainers. As a maintainer you may freely
push to your package(s) and initiate builds for them, which will be pushed to
the unstable repository. You can watch builds at the [Solus Package Build Status Page](https://build.getsol.us/)

If you're submitting a `package.yml` build, ensure you also commit the `pspec_$ARCH.xml`
file, as builds are created from git tags.

    cd $somepkg
    make publish

Maintainership
-------------
Note that the infrastructure (including git pushes) is entirely locked
to your public key. Pushing changes is not possible unless you have maintainer
access. The same is also true of `make publish`.

To request maintainer rights for a repository, it is expected that some level
of contribution/maintenance has already happened by way of testing/patching, and
there is reasonable trust demonstrated to "hand the keys" over to a repository.

Currently, the request mechanism is to [catch JoshStrobl on IRC](irc://irc.freenode.net/#Solus-Dev)
Bluntly put, it is far easier to grant access to active community members than those
unknown to the project.

Finally, note that the management reserve the right to revoke access at any time,
in order to preserve project safety and integrity.

solbuild/setup
-------------

Install `solbuild` from the main repository.. *All* builds are performed in
the unstable repository, so `unstable-x86_64` is the default build profile.

Install `solbuild-config-unstable` to lock builds to the unstable repository.

See `man solbuild` for further details.
