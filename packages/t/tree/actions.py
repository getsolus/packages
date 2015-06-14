#!/usr/bin/python


from pisi.actionsapi import autotools,get

def build():
    autotools.make()

def install():
    autotools.install()
