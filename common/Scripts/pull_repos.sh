#!/bin/bash

where=`realpath $(dirname $0)`
while IFS='' read -r line || [[ -n $line ]]; do
    pname=`basename ${line}`
    if [[  -d "$pname" ]]; then
        pushd "$pname"
        git pull --rebase
        popd
    fi

done < "${where}/../packages"
