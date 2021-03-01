#!/bin/bash
# Bail on error
set -e

COMMITLOG="imagemagick 7.0.11-2"

REPO=$PWD
C="\e[33m"
R="\033[m"
PKGS=""

if [ "${1}" == "setup" ]; then

    if [ -z "${2}" ]; then
        echo "Missing repository name"
        exit 1
    fi

    REPO=~/repo/${2}
    rm -rf ${REPO}
    mkdir -p ${REPO}
    cd ${REPO}

    git clone https://dev.getsol.us/source/common.git
    ln -s common/Makefile.common .
    ln -s common/Makefile.toplevel Makefile
    ln -s common/Makefile.iso .

    cp ~/repo/sunny.sh .
    touch pkgs.txt
fi

PKGS=$(grep -v '^#' < ${REPO}/pkgs.txt)

if [ "${1}" == "bump" ]; then
    cd ${REPO}
    for i in ${PKGS}; do
        git clone "https://dev.getsol.us/source/${i}.git"
        pushd ${i}
            git remote set-url origin "https://dev.getsol.us/source/${i}.git"
            git remote set-url --push origin "ssh://vcs@dev.getsol.us:2222/source/${i}.git"
            make bump
            
            if [ -f component.xml ] && [ -f package.yml ]; then
                echo -e "${C}component must be added in package.yml of ${i}${R}"
            fi
        popd
    done
fi

if [ "${1}" == "build" ]; then
    cd ${REPO}
    for i in ${PKGS}; do
        echo -e "${C}BEGIN ============================ ${i} ============================ BEGIN${R}"
        pushd ${i}
            sudo solbuild build -p local-unstable-x86_64 -t -m 7G
            make abireport
            sudo mv *.eopkg /var/lib/solbuild/local/
        popd
        echo -e "${C}END ============================= ${i} ============================= END${R}"
    done
    pushd /var/lib/solbuild/local
        sudo solbuild index
    popd
fi

if [ "${1}" == "validate" ]; then
    cd ${REPO}
    for i in ${PKGS}; do
        pushd ${i}
            make clean
            git diff
            git add *
            git commit --signoff -m "Safety rebuild ${i} for ${COMMITLOG}"
        popd
    done
fi

if [ "${1}" == "push" ]; then
    cd ${REPO}
    for i in ${PKGS}; do
        pushd ${i}
            make publish
            ~/repo/WAIT_FOR_SYNC.sh
        popd
    done
fi

if [ "${1}" == "land" ]; then
    cd ${REPO}
    for i in ${PKGS}; do
        pushd ${i}
            arc land
            make publish
            ~/repo/WAIT_FOR_SYNC.sh
        popd
    done
fi



if [ "${1}" == "stash" ]; then
    cd ${REPO}
    for i in ${PKGS}; do
        pushd ${i}
            git stash
            make pull
            git stash pop
        popd
    done
fi
