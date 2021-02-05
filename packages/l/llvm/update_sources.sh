#!/bin/bash

LLVMVERSION="$1"

if [[ -z $LLVMVERSION ]]; then
    echo "Usage: $0 <version number>"
    exit 1
fi

BASEURI="https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVMVERSION}"

LINKS="$BASEURI/llvm-${LLVMVERSION}.src.tar.xz
    $BASEURI/clang-${LLVMVERSION}.src.tar.xz
    $BASEURI/compiler-rt-${LLVMVERSION}.src.tar.xz
    $BASEURI/lld-${LLVMVERSION}.src.tar.xz
    $BASEURI/clang-tools-extra-${LLVMVERSION}.src.tar.xz
    $BASEURI/libcxx-${LLVMVERSION}.src.tar.xz
    $BASEURI/libcxxabi-${LLVMVERSION}.src.tar.xz
    $BASEURI/openmp-${LLVMVERSION}.src.tar.xz"

pushd /tmp
wget -nv ${LINKS} > /dev/null
for i in ${LINKS}; do
    j=`basename ${i}`
    echo "    - ${i} : `sha256sum ${j} | awk '{ print $1 }'`"
    rm ${j}
done
popd
