#!/usr/bin/python


from pisi.actionsapi import get, pisitools, pythonmodules

def install():
    pythonmodules.install()

    for i in ["yupdate.py", "ybump.py"]:
        pisitools.insinto("/usr/share/ypkg", "scripts/" + i)
