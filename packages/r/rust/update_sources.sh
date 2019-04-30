#!/bin/sh
# Fetch the latest sources and sha256sums automagically

VERSION=$1

alias silent_wget='wget -q'

mkdir /tmp/rust; cd /tmp/rust
silent_wget https://raw.githubusercontent.com/rust-lang/rust/${VERSION}/src/stage0.txt
DATE=$(grep '^date' stage0.txt | awk '{ print $2 }')
RUSTV=$(grep '^rustc' stage0.txt | awk '{ print $2 }')
CARGOV=$(grep '^cargo' stage0.txt | awk '{ print $2 }')

URLS="
https://static.rust-lang.org/dist/rustc-${VERSION}-src.tar.gz
https://static.rust-lang.org/dist/${DATE}/rustc-${RUSTV}-x86_64-unknown-linux-gnu.tar.gz
https://static.rust-lang.org/dist/${DATE}/rust-std-${RUSTV}-x86_64-unknown-linux-gnu.tar.gz
https://static.rust-lang.org/dist/${DATE}/cargo-${CARGOV}-x86_64-unknown-linux-gnu.tar.gz
"

for i in ${URLS}; do
    silent_wget ${i}.sha256
done
for i in ${URLS}; do
    j=$(basename ${i})
    echo "    - ${i} : $(awk '{ print $1 }' ${j}.sha256)"
done
rm -rf /tmp/rust
