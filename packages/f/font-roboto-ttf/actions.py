#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import glob

FontDir = "/usr/share/fonts/truetype/roboto/"
WorkDir = "."

def install():
    for i in glob.glob("*.ttf"):
        pisitools.insinto(FontDir, i)
    shelltools.system("chmod 644 -R %s/%s" % (get.installDIR(), FontDir))
