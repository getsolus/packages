#!/bin/sh

# Check the current stable revision from https://josm.openstreetmap.de/wiki/Download
revision=$1
src_name=josm-$revision

svn export -r $revision https://josm.openstreetmap.de/svn/trunk /tmp/$src_name
if [ $? -eq 0 ]; then
	tar cJf $src_name.tar.xz -C /tmp $src_name
	sha256sum $src_name.tar.xz
fi
rm -rf /tmp/$src_name
