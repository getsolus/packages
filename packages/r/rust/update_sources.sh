# Fetch the latest sources and sha256sums automagically
VERSION=1.31.1
mkdir /tmp/rust; cd /tmp/rust

wget https://raw.githubusercontent.com/rust-lang/rust/${VERSION}/src/stage0.txt
DATE=`cat stage0.txt | grep ^date | awk '{ print $2 }'`
RUSTV=`cat stage0.txt | grep ^rustc | awk '{ print $2 }'`
CARGOV=`cat stage0.txt | grep ^cargo | awk '{ print $2 }'`

URLS="
https://static.rust-lang.org/dist/rustc-${VERSION}-src.tar.gz
https://static.rust-lang.org/dist/${DATE}/rustc-${RUSTV}-x86_64-unknown-linux-gnu.tar.gz
https://static.rust-lang.org/dist/${DATE}/rust-std-${RUSTV}-x86_64-unknown-linux-gnu.tar.gz
https://static.rust-lang.org/dist/${DATE}/cargo-${CARGOV}-x86_64-unknown-linux-gnu.tar.gz
"

for i in ${URLS}; do
    wget ${i}.sha256
done
for i in ${URLS}; do
    j=`basename ${i}`
    echo "    - ${i} : `cat ${j}.sha256 | awk '{ print $1 }'`"
done
rm -rf /tmp/rust
