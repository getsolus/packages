#!/bin/sh

[ -z "$JAVA_HOME" ] && export JAVA_HOME=/usr/lib64/openjdk-11

exec /usr/share/bazel/bazel "$@"
