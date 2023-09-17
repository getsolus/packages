#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is used for constructing modaliases for piper from libratbag
#  It is by no means robust or clean.
#
#  Copyright © 2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import GLib
import os

def push_sect(blob, aliases):
    splits = blob.split(":")
    id = splits[0]
    if id != "usb" and id != "bluetooth":
        return
    # Set piper name because we want users installing that, not the library
    modalias = "alias {}:v{}*{}* piper piper".format(id, splits[1].upper(), splits[2].upper())
    aliases.append(modalias)

def main():
    aliases = []

    for item in sorted(os.listdir("/usr/share/libratbag")):
        if not item.endswith(".device"):
            continue
        kfile = GLib.KeyFile()
        fpath = os.path.join("/usr/share/libratbag", item)
        kfile.load_from_file(fpath, 0)
        sects = kfile.get_string_list("Device", "DeviceMatch")
        for blob in sects:
            push_sect(blob, aliases)

    aliases.sort()
    with open("piper.modaliases", "w") as outp:
        for line in aliases:
            outp.write(line + '\n')

if __name__ == "__main__":
    main()
