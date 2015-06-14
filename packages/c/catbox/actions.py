
#!/usr/bin/python


from pisi.actionsapi import pythonmodules

def install():
    pythonmodules.install("--enable-pcre")
