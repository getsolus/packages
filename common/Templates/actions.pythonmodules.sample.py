#!/usr/bin/python

from pisi.actionsapi import pythonmodules, pisitools


def build():
    pythonmodules.compile()


def check():
    pythonmodules.compile("test")


def install():
    pythonmodules.install()

    #EXTRADOCS#
