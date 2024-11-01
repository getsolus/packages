# Rebuilding ypkg after an eopkg build

If changes are made to the upstream eopkg git ref, `ypkg` should generally be rebuilt, as some of its binaries depend on and import python-eopkg code from the present package.

This can be omitted if the upstream changes do not affect the code.
