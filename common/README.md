Getting setup
------------

    git clone https://git.solus-project.com/common
    ln -sv common/Makefile.common .
    ln -sv  common/Makefile.toplevel Makefile

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

    # Ensure evobuild is setup..
    cd $somepkg
    make

Submitting a build
-----------------
Submission is only possible for maintainers. As a maintainer you may freely
push to your package(s) and initiate builds for them, which will be pushed to
the unstable repository. You can watch builds at the [Solus Package Build Status Page](https://build.solus-project.com/)

If you're submitting a `package.yml` build, ensure you also commit the `pspec_$ARCH.xml`
file, as builds are created from git tags.

    cd $somepkg
    make publish

evobuild/setup
-------------

Solus users will have evobuild already available. *All* builds are performed in
the unstable repository, so `unstable-x86_64` is the default build profile. If
evobuild emits the following warning, you will need to initialise the profile:

    Building $pkg for unstable-x86_64
    Did you forget to init unstable-x86_64 profile?

This can be remedied as follows (note this may take some time depending on your
connection)

    sudo evobuild init -p unstable_x86-64
