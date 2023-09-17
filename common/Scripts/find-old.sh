#!/bin/sh

if [ -e "old.lst" ]; then
    rm old.lst
fi

for f in `ls -1`; do
    if [ -d "$f/.git" ]; then
        pushd $f
        dt=`git log -1 --format=%cs`
        popd > /dev/null
        printf "%s %s\n" $dt $f >> old.lst
    fi
done

sort -n old.lst > old-sorted.lst
