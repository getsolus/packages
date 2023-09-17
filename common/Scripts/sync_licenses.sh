#!/bin/bash

fail_exit(){
        echo "$1"
        exit 1
}

git clone https://github.com/spdx/license-list-XML.git --depth=1 || fail_exit "Failed to clone"

if [[ -e "licenses.spdx" ]];
        then rm -v licenses.spdx
fi

pushd license-list-XML/src

for i in *.xml ; do
        sum=`sha1sum "${i}"|cut -f 1 -d ' '`
        nom=`echo "$i" | sed 's@\.xml$@@'`
        echo -e "${sum}\t${nom}" >> ../../licenses.spdx
done
popd
rm -rf license-list-XML
