#!/usr/bin/env python
import pisi.db.packagedb
import pisi.config

if __name__ == "__main__":
    config = pisi.config.Config()
    distro = config.values.general.distribution
    db = pisi.db.packagedb.PackageDB()
    bads = dict()
    goods = dict()
    for pkgname in db.list_packages(None):
        pkg = db.get_package(pkgname)
        pdistro = pkg.distribution
        if pdistro != distro:
            src = pkg.source.name
            if src not in bads:
                bads[src] = list()
            bads[src].append(pkg.name)
        else:
            src = pkg.source.name
            if src not in goods:
                goods[src] = list()
            goods[src].append(pkg.name)
    binCount = 0
    for src in bads:
        binCount += len(bads[src])
        print "%s -  %s packages" % (src, len(bads[src]))
    print
    top = len(bads.keys()) + len(goods.keys())
    print "%s of %s source packages have an incorrect distribution string (%s binary)" % (len(bads.keys()), top, binCount)
    print "%s have the correct distribution string" % len(goods.keys())
    print "Progress: %0.2f%%" % ((float(len(goods.keys())) / float(top))*100)
