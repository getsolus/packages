#!/bin/bash
for i in `find -type f -name "*.qml"`; do
    if ! [ -a "${i}"c ]; then
        qmlcachegen --target-architecture=x86_64 --target-abi=x86_64-little_endian-lp64 -o "${i}"c "${i}"
    fi
done
