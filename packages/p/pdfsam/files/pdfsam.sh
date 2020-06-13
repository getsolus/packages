#!/bin/sh

if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME=/usr/lib64/openjdk-11
fi

exec $JAVA_HOME/bin/java -jar /usr/share/pdfsam/pdfsam.jar "$@"
