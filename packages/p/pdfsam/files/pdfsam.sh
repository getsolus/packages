#!/bin/sh

if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME=/usr/lib64/openjdk-17
fi

exec $JAVA_HOME/bin/java -jar /usr/share/pdfsam/pdfsam.jar -Xmx512M -Dapp.name="pdfsam-basic" -Dapp.pid="$$" -Dapp.home=/usr/share/pdfsam -Dbasedir=/usr/share/pdfsam -Dprism.lcdtetxt=false  "$@"
