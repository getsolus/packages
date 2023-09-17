#!/usr/bin/env python2.7
#
# Helper script to find rebuilds not yet done against a specific release
# of the package.
# Originally added so that kyrios can track down missing libpng rebuilds.
# This works on the premise of binary dependencies in Solus automatically
# being added with a releaseFrom=$currentRelease so that we force an update
# when we rebuild against an updated component.
#
# Script must be run with unstable repository configured so it can check
# the index correctly.

import pisi.api

TARGET_PACKAGE = "libpng"
TARGET_RELEASE = 14

class StrayAccumulator:

    repoDB = None
    rebuilt = None
    pending = None
    unknown = None

    def __init__(self, package, release):
        self.package = package
        self.release = release

        self.rebuilt = set()
        self.pending = set()
        self.unknown = set()

        # So we have a view of the repo
        self.repoDB = pisi.db.packagedb.PackageDB()

    def calculate(self):
        """ Attempt to assign all the buckets """
        revdeps = self.repoDB.get_rev_deps(self.package)
        package = self.repoDB.get_package(self.package)

        # Determine the *active* pkgRelease
        pkgRelease = int(package.release)

        for (pkgID, dependency) in revdeps:
            fromRel = None

            # Most will depend *from* a release
            if dependency.releaseFrom:
                fromRel = int(dependency.releaseFrom)
            elif dependency.release:
                fromRel = int(dependency.release)
                if fromRel != pkgRelease:
                    print("WARNING: Invalid dependency on {} release {} == {}".format(self.package, fromRel, pkgID))
                    self.unknown.add(pkgID)
                    continue

            # Manually added runtime dependency
            if not fromRel:
                self.unknown.add(pkgID)
                continue

            # If it depends on an old guy, it's pending, otherwise, it's rebuilt
            if fromRel < pkgRelease:
                self.pending.add(pkgID)
            else:
                self.rebuilt.add(pkgID)

    def dump(self):
        """ Emit statistics now """

        # Dump the rebuilt status
        if len(self.rebuilt) > 0:
            print("{} packages have been rebuilt properly\n".format(
                  len(self.rebuilt)))

        # Dump the pending set
        if len(self.pending) > 0:
            pending = list(self.pending)
            pending.sort()
            print("{} packages pending a rebuild\n".format(len(self.pending)))
            for p in pending:
                print(" - {}".format(p))

        if len(self.unknown) < 1:
            return

        unknown = list(self.unknown)
        unknown.sort()
        print("\n\n{} packages have manually added runtime dependency\n".format(len(unknown)))
        for u in unknown:
            print("  - {}".format(u))

def main():
    accum = StrayAccumulator(TARGET_PACKAGE, TARGET_RELEASE)
    accum.calculate()
    accum.dump()

if __name__ == "__main__":
    main()
