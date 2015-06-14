#!/usr/bin/python


from pisi.actionsapi import get, cmaketools


def setup():
    cmaketools.configure()


def build():
    cmaketools.make()


def install():
    cmaketools.install()

    
