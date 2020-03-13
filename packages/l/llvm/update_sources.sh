#!/bin/bash
LLVMVERSION=9.0.1
LINKS="https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVMVERSION}/llvm-${LLVMVERSION}.src.tar.xz
    https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVMVERSION}/clang-${LLVMVERSION}.src.tar.xz
    https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVMVERSION}/compiler-rt-${LLVMVERSION}.src.tar.xz
    https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVMVERSION}/lld-${LLVMVERSION}.src.tar.xz
    https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVMVERSION}/clang-tools-extra-${LLVMVERSION}.src.tar.xz
    https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVMVERSION}/libcxx-${LLVMVERSION}.src.tar.xz
    https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVMVERSION}/libcxxabi-${LLVMVERSION}.src.tar.xz
    https://github.com/llvm/llvm-project/releases/download/llvmorg-${LLVMVERSION}/openmp-${LLVMVERSION}.src.tar.xz
"
pushd /tmp
wget ${LINKS} > /dev/null
for i in ${LINKS}; do
    j=`basename ${i}`
    echo "    - ${i} : `sha256sum ${j} | awk '{ print $1 }'`"
    rm ${j}
done
popd
