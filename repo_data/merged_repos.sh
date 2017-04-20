#!/bin/bash

for i in components.xml distribution.xml groups.xml; do
    intltool-merge --xml-style ../po/ $i.in $i
done
