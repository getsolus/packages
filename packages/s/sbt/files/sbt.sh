#!/bin/bash

if [[ -z "${SBT_OPTS}" ]]; then
  SBT_OPTS="-Xms512M -Xmx1536M -Xss1M -XX:+CMSClassUnloadingEnabled"
fi

if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME=/usr/lib64/openjdk-21
fi

exec $JAVA_HOME/bin/java $SBT_OPTS -jar /usr/share/sbt/sbt.jar "$@"
