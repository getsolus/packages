#!/bin/bash
set -e
PACKAGE=$1
REF=$2

mkdir staging
export staging=`realpath staging`

export GOPATH=$staging

# Clone package ourselves, check out correct tags
mkdir -p $staging/src
git clone https://$PACKAGE $staging/src/$PACKAGE
pushd staging/src/$PACKAGE
git checkout -b goget-staging-$REF $REF
git checkout -b fakeorigin/$REF
git checkout goget-staging-$REF
git branch -u fakeorigin/$REF
popd

go get -d -f -u -v -t -insecure $PACKAGE/...
find $staging/src -name ".git" -type d | xargs -I{} rm -rvf {}

name=`basename $PACKAGE`
version=$REF
mv staging $name-$version
tar cvf $name-$version.tar $name-$version
xz -6 $name-$version.tar
rm -rf $name-$version
