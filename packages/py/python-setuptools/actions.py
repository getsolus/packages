
#!/usr/bin/python


from pisi.actionsapi import pythonmodules, pisitools


def install():
    pythonmodules.install()
    pythonmodules.install(pyVer="3")
