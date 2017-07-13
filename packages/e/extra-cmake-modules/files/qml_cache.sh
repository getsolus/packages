#!/bin/bash
for i in `find -type f -name "*.qml"`; do
    if ! [ -a "${i}"c ]; then
        echo "Generating QML cache file ${i}"
        qmlcachegen --target-architecture=x86_64 --target-abi=x86_64-little_endian-lp64 -o "${i}"c "${i}"
    fi
done
