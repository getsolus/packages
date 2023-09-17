#!/bin/sh

if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME=/usr/lib64/openjdk-17
fi

exec /usr/share/jabref/bin/JabRef "$@"
