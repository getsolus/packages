
#!/usr/bin/python


from pisi.actionsapi import shelltools, get, autotools, pisitools
import glob

WorkDir = "ttf-droid-1.00~b112+dfsg+1"

FontDir = "/usr/share/fonts/truetype/droid/"

def install():

    for i in glob.glob("*.ttf"):
        pisitools.insinto(FontDir, i)

        pisitools.dodoc("README")
