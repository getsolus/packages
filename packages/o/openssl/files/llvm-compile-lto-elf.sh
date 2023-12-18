#!/usr/bin/bash -eu

# Adapted from
# https://salsa.debian.org/pkg-llvm-team/llvm-toolchain/-/blob/snapshot/debian/llvm-compile-lto-elf.sh?ref_type=heads

CLANG_FLAGS=$@

if test -z $NJOBS; then
    echo "NJOBS isn't set"
    exit 1
fi

export CLANG_BIN="${CLANG_BIN:-'/usr/bin/clang'}"
export LLVM_AR_BIN="${LLVM_AR_BIN:-'/usr/bin/llvm-ar'}"
export LLVM_BCANALYZER_BIN="${LLVM_BCANALYZER_BIN:-'/usr/bin/llvm-bcanalyzer'}"

check_convert_bitcode () {
    local file_name=$(realpath ${1})
    local file_type=$(file ${file_name})
    shift
    CLANG_FLAGS="$@"

    if [[ "${file_type}" == *"LLVM IR bitcode"* ]]; then
        # check for an indication that the bitcode was
        # compiled with -flto
        LLVM_BCANALYZER_BIN -dump ${file_name} | grep -xP '.*\-flto((?!-fno-lto).)*' 2>&1 > /dev/null
        if [ $? -eq 0 ]; then
            echo "Compiling LLVM bitcode file ${file_name}."
            CLANG_BIN -fno-lto -opaque-pointers -Wno-unused-command-line-argument \
                -x ir ${file_name} -c -o ${file_name}
        fi
    elif [[ "${file_type}" == *"current ar archive"* ]]; then
        echo "Unpacking ar archive ${file_name} to check for LLVM bitcode components."
        # create archive stage for objects
        local archive_stage=$(mktemp -d)
        local archive=${file_name}
        pushd ${archive_stage}
        ar x ${archive}
        for archived_file in $(find -not -type d); do
            check_convert_bitcode ${archived_file} ${CLANG_FLAGS}
            echo "Repacking ${archived_file} into ${archive}."
            LLVM_AR_BIN r ${archive} ${archived_file}
        done
        popd
    fi
}

echo "Checking for LLVM bitcode artifacts"
export -f check_convert_bitcode
find "$installdir" -type f -name "*.[ao]" -print0 | \
    xargs -0 -r -n1 -P$NCPUS bash -c "check_convert_bitcode \$@ $CLANG_FLAGS" ARG0
