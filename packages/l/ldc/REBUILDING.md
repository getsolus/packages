When upgrading between releases a two-stage bootstrap must be performed, this should be left enabled.
- 1. Perform a bootstrap build with `BUILD_SHARED_LIBS=OFF`.
- 2. Build against the bootstraped ldc with `D_COMPILER=$workdir/ldc-bootstrap/bin/ldmd2` and `BUILD_SHARED_LIBS=BOTH`.

Re-bootstrapping against a pre-built binary is also possible but not preferred when updating.

When rebuilding against a new LLVM/Clang version a few options are present.
- 1. Re-bootstrap against a pre-built ldc binary.
- 2. Link against LLVM/Clang statically _before_ they are updated, then rebuild against the new version dynamically as usual.
- 3. Bootstrap with gcc by checking out the `ltsmaster` branch, this branch is not always updated on time for new releases.
