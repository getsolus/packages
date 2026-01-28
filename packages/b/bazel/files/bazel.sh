#!/bin/sh

[ -z "$JAVA_HOME" ] && export JAVA_HOME=/usr/lib64/openjdk-21

exec /usr/share/bazel/bazel "$@"
