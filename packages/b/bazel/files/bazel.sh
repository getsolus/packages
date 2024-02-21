#!/bin/sh

[ -z "$JAVA_HOME" ] && export JAVA_HOME=/usr/lib64/openjdk-17

exec /usr/share/bazel/bazel "$@"
