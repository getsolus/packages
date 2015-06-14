#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  yauto.py
#  
#  Copyright 2013 Ikey Doherty <ikey@solusos.com>
#  Copyright 2015 Ikey Doherty <iikey@solus-project.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
import urllib2
import hashlib

def download_file(url):
    file_name = url.split('/')[-1]
    output = file_name
    u = urllib2.urlopen(url)
    f = open(output, 'wb')
    meta = u.info()

    headers = meta.getheaders("Content-Length")
    file_size = 0
    if len(headers) >= 1:
        file_size = int(headers[0])

    file_size_dl = 0
    block_sz = 8192
    while True:
            buffer = u.read(block_sz)
            if not buffer:
                    break

            file_size_dl += len(buffer)
            f.write(buffer)
            if file_size > 0:
                status = r" [%3.2f%%] %s/%s %s" % (file_size_dl * 100. / file_size, sizeof_fmt(file_size_dl), sizeof_fmt(file_size), file_name)
            else:
                status = r"  %s/unknown_size %s" % (sizeof_fmt(file_size_dl), file_name)
            status = status + chr(8)*(len(status)+1)
            print status,

    print "\n"
    f.close()

def sizeof_fmt(num):
        for x in ['bytes','KB','MB','GB']:
                if num < 1024.0:
                        return "%3.1f%s" % (num, x)
                num /= 1024.0
        return "%3.1f%s" % (num, 'TB')

def get_sha256sum (filename):
		sh = hashlib.sha256 ()
		f = open (filename, "r")
		sh.update (f.read())
		ret = sh.hexdigest ()
		f.close ()
		
		return ret

def get_sha1sum (filename):
		sh = hashlib.sha1 ()
		f = open (filename, "r")
		sh.update (f.read())
		ret = sh.hexdigest ()
		f.close ()
		
		return ret

