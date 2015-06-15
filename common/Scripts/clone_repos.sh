#!/bin/bash

where=`realpath $(dirname $0)`
while IFS='' read -r line || [[ -n $line ]]; do
    pname=`basename ${line}`
    if [[ ! -d "$pname" ]]; then
        git clone "https://git.solus-project.com/$line"
        pushd "$pname"
        git remote set-url origin "https://git.solus-project.com/$line"
        git remote set-url --push origin "git@solus-project.com:$line"
        popd
    fi

done < "${where}/../packages"
