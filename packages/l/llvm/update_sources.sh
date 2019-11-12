#!/bin/bash
LLVMVERSION=9.0.0
LINKS="https://releases.llvm.org/${LLVMVERSION}/llvm-${LLVMVERSION}.src.tar.xz
    https://releases.llvm.org/${LLVMVERSION}/cfe-${LLVMVERSION}.src.tar.xz
    https://releases.llvm.org/${LLVMVERSION}/compiler-rt-${LLVMVERSION}.src.tar.xz
    https://releases.llvm.org/${LLVMVERSION}/lld-${LLVMVERSION}.src.tar.xz
    https://releases.llvm.org/${LLVMVERSION}/clang-tools-extra-${LLVMVERSION}.src.tar.xz
    https://releases.llvm.org/${LLVMVERSION}/libcxx-${LLVMVERSION}.src.tar.xz
    https://releases.llvm.org/${LLVMVERSION}/libcxxabi-${LLVMVERSION}.src.tar.xz
    https://releases.llvm.org/${LLVMVERSION}/openmp-${LLVMVERSION}.src.tar.xz
"
pushd /tmp
wget ${LINKS} > /dev/null
for i in ${LINKS}; do
    j=`basename ${i}`
    echo "    - ${i} : `sha256sum ${j} | awk '{ print $1 }'`"
    rm ${j}
done
popd
