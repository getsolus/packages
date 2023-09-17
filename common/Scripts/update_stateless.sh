#!/bin/sh

if [ -e "STATELESSNESS" ]; then
    rm STATELESSNESS
fi

touch STATELESSNESS

pushd ..

for f in `ls -1`; do
    if [ -e "$f/pspec.xml" ]; then
        grep -H \>/etc $f/pspec.xml >> common/STATELESSNESS
    fi
    if [ -e "$f/pspec_x86_64.xml" ]; then
        grep -H \>/etc $f/pspec_x86_64.xml >> common/STATELESSNESS
    fi
done

popd

exit 0