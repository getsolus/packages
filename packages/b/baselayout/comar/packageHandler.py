#!/usr/bin/python
import piksemel
import os
import os.path

LIBRARY_DIRS = ["/usr/lib64", "/usr/lib64/avx2", "/usr/lib", "/usr/lib/avx2", "/lib", "/lib64", "/lib32", "/usr/lib32"]

def updateLdConfig(filepath):
    parse = piksemel.parse(filepath)

    shouldConf = False

    for xmlfile in parse.tags("File"):
        path = xmlfile.getTagData("Path")
        if not path.startswith("/"):
            path = "/%s" % path # Just in case
        if path.startswith("/etc/ld.so.conf"):
            shouldConf = True
            break
        if path.startswith("/usr/share/ld.so.conf"):
            shouldConf = True
            break
        if not ".so" in path:
            continue
        if os.path.dirname(path) in LIBRARY_DIRS:
            shouldConf = True
            break

    if shouldConf:
        try:
            os.system("/sbin/ldconfig")
        except:
            pass

def setupPackage(metapath, filepath):
    try:
        updateLdConfig(filepath)
    except:
        pass


def postCleanupPackage(metapath, filepath):
    try:
        updateLdConfig(filepath)
    except:
        pass

