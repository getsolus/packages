
#!/usr/bin/python


from pisi.actionsapi import pythonmodules, autotools, shelltools, get, pisitools

def install():
    pythonmodules.install()
    # Weird man path, move the file then remove the extra wrong path
    pisitools.domove("/usr/man/man1/bzr.1", "/usr/share/man/man1/bzr.1")
    pisitools.removeDir("/usr/man")
