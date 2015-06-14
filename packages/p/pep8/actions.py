#!/usr/bin/python
from pisi.actionsapi import pythonmodules


def build():
    pythonmodules.compile()


def install():
    pythonmodules.install()
