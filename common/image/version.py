#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  version.py - Create new candidate version
#  
#  Copyright 2015 Ikey Doherty <ikey@solus-project.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
import os
from datetime import date
import time

# Set to 1 for stable builds in future
MAJOR = "0"

def get_image_version():
    today = date.fromtimestamp(time.time())
    iso = today.isocalendar()

    iso_year = iso[0]
    iso_week = iso[1]
    iso_day = iso[2]
    
    build_id = 0

    version = None

    while (True):
        version = "%s.%s%s.%s.%s" % (MAJOR, iso_year, iso_week, iso_day, build_id)
        rel_path = os.path.join("./releases", version)
        if not os.path.exists(rel_path):
            break
        build_id += 1
    return version

if __name__ == "__main__":
    print get_image_version()
