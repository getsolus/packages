#!/bin/sh

if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME=/usr/lib64/openjdk-21
fi

export JAB_REF_OPTS="--patch-module org.jabref=/usr/share/jabref/resources/main"

exec /usr/share/jabref/bin/JabRef "$@"
