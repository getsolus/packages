#!/usr/bin/env bash

pushd po

for i in *.po ; do
    msgmerge ${i} repo_data.pot -o ${i}
    msgattrib --no-obsolete -o ${i} ${i}
done
