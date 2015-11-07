#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools
import os

WordsFile = "../cracklib-words-2.9.6.gz"

def setup():
    autotools.configure ("--disable-static")

def build():
    autotools.make ()

def install():
    autotools.rawInstall ("DESTDIR=%s" % get.installDIR())

    pisitools.insinto ("/usr/share/dict", WordsFile, "cracklib-words.gz")

    wd = os.getcwd ()
    os.chdir ("%s/usr/share/dict" % get.installDIR())
    os.system ("gunzip -c cracklib-words.gz > cracklib-words")
    os.chdir (wd)

    pisitools.dosym ("/usr/share/dict/cracklib-words", "/usr/share/dict/words")

    pisitools.dodoc ("AUTHORS", "ChangeLog")

    path = "%s:%s/usr/sbin" % (os.environ["PATH"], get.installDIR())
    libpath = "/lib:/usr/lib::%s/usr/lib" % get.installDIR()
    os.system ("LD_LIBRARY_PATH=%s PATH=%s %s/usr/sbin/create-cracklib-dict -o %s/usr/share/cracklib/pw_dict %s/usr/share/dict/cracklib-words" % (libpath, path, get.installDIR(), get.installDIR(), get.installDIR()) )
