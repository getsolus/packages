#!/usr/bin/env python2.7
#
# Helper script to find any  packages not rebuilt in a while

import pisi.db
import datetime
import time

DAY = 86400  # 86400 seconds in a day
PERIOD = 120 * DAY  # 31 days is old

class HistoryTeacher:

    pdb = None
    tipbucket = None
    stamp = None

    def __init__(self):
        self.pdb = pisi.db.packagedb.PackageDB()
        self.tipbucket = dict()
        self.stamp = float(time.time())

    def assess(self):
        """ Walk all known packages in repo """
        for key in self.pdb.list_packages(None):
            self.maybe_push(key)

    def maybe_push(self, key):
        """ Maybe assign the package to the tipbucket """
        if key in self.tipbucket:
            return
        if not self.pdb.has_package(key):
            return
        pkg = self.pdb.get_package(key)
        update = pkg.history[0]
        whence = self.sensible_date(update.date)
        self.tipbucket[key] = whence

    def sensible_date(self, shittyInput):
        """ Return probably wonky date into a usable timestamp """
        try:
            whence = datetime.datetime(*time.strptime(shittyInput, "%Y-%m-%d")[0:6])
        except:
            try:
                whence = datetime.datetime(*time.strptime(shittyInput, "%d-%m-%Y")[0:6])
            except:
                whence = datetime.datetime(*time.strptime(shittyInput, "%m-%d-%Y")[0:6])
        return time.mktime(whence.timetuple())

    def dumpDelinquints(self):
        """ Dump the nasty fecks out """
        oldFogies = []
        for key in self.tipbucket:
            # Only show source names instead of package names
            pkg = self.pdb.get_package(key)
            sourceName = pkg.source.name
            if sourceName in oldFogies:
                continue

            timestamp = self.tipbucket[key]
            diff = self.stamp - timestamp
            if diff < PERIOD:
                continue

            # Store the source name only
            oldFogies.append(sourceName)

        # Sort for display
        oldFogies.sort()
        print("Not rebuilt in 31 days or more:\n\n")
        for fogie in oldFogies:
            print(" > {}".format(fogie))

def main():
    teacher = HistoryTeacher()
    teacher.assess()
    teacher.dumpDelinquints()
    pass

if __name__ == "__main__":
    main()
