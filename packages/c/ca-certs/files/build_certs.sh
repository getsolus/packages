#!/bin/bash

certhost='http://mxr.mozilla.org'                        &&
certdir='/mozilla/source/security/nss/lib/ckfw/builtins' &&
url="$certhost$certdir/certdata.txt?raw=1"               &&

curl $url -o certdata.txt                &&
unset certhost certdir url               &&
./make-ca.sh                             &&
./remove-expired-certs.sh certs
