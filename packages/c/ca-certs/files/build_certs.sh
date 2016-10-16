#!/bin/bash

url="http://anduin.linuxfromscratch.org/BLFS/other/certdata.txt"

curl $url -o certdata.txt                &&
unset url                                &&
./make-ca.sh                             &&
./remove-expired-certs.sh certs
