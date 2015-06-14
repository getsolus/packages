#!/bin/bash

IANA_VERSION=2.30

wget http://sethwklein.net/iana-etc-$IANA_VERSION.tar.bz2
tar xvf iana-etc-$IANA_VERSION.tar.bz2

pushd iana-etc-$IANA_VERSION

sed -i 's:file=protocol-numbers:file=protocol-numbers/protocol-numbers.txt:' Makefile

make get
LC_ALL=C make
make test

cp {services,protocols} ../

popd

# Cleanup
rm -rf iana-etc-$IANA_VERSION
