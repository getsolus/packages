#!/bin/bash
VERSION=${1}
MJRVERSION=${VERSION%.*.*}
GITVERSION=$(echo $VERSION | tr '.' '_')

LINKS="https://ftp.gnu.org/gnu/gcc/gcc-${VERSION}/gcc-${VERSION}.tar.xz
    https://github.com/gcc-mirror/gcc/compare/gcc-${GITVERSION}-release...gcc-${MJRVERSION}-branch.patch"

mkdir -p /tmp/gcc-tmp
pushd /tmp/gcc-tmp
wget ${LINKS} > /dev/null
    for i in ${LINKS}; do
        j=`basename ${i}`
        echo "    - ${i} : `sha256sum ${j} | awk '{ print $1 }'`"
        rm ${j}
    done
popd

rm -rf /tmp/gcc-tmp
