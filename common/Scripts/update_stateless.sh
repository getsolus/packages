#!/bin/sh

if [ -e "STATELESSNESS" ]; then
    rm STATELESSNESS
fi

touch STATELESSNESS

pushd ../packages

for f in `ls`; do
    pushd $f
    for p in `ls`; do
        if [ -e "$p/pspec.xml" ]; then
            grep -H \>/etc $p/pspec.xml >> ../../common/STATELESSNESS
        fi
        if [ -e "$p/pspec_x86_64.xml" ]; then
            grep -H \>/etc $p/pspec_x86_64.xml >> ../../common/STATELESSNESS
        fi
    done
    popd
done

popd

exit 0
