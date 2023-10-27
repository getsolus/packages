#!/bin/bash

#
# setup phase
#
IANA_VERSION=20231019

echo "WORKDIR is ${PWD}."
wget https://github.com/Mic92/iana-etc/releases/download/${IANA_VERSION}/iana-etc-${IANA_VERSION}.tar.gz
wget https://github.com/Mic92/iana-etc/releases/download/${IANA_VERSION}/iana-etc-${IANA_VERSION}.tar.gz.sha256

# Ensure that we have a good download
EXPECTED_SHA256SUM="$(cat iana-etc-${IANA_VERSION}.tar.gz.sha256)"
ACTUAL_SHA256SUM="$(sha256sum iana-etc-20231019.tar.gz| cut -d ' ' -f1)"
if [[ ! "${EXPECTED_SHA256SUM}" == "${ACTUAL_SHA256SUM}" ]]; then
    echo "sha256sum mismatch for iana-etc-${IANA_VERSION}.tar.gz.sha256, exiting!" && exit 1
fi
unset EXPECTED_SHA256SUM
unset ACTUAL_SHA256SUM

tar -xvf iana-etc-${IANA_VERSION}.tar.gz
pushd iana-etc-$IANA_VERSION

#
# install phase
#
cp {services,protocols} ../
popd

#
# cleanup phase
#
rm -rvf iana-etc-$IANA_VERSION*
