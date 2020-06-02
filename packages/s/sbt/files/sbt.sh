#!/bin/bash
if [[ -z "${SBT_OPTS}" ]]; then
  SBT_OPTS="-Xms512M -Xmx1536M -Xss1M -XX:+CMSClassUnloadingEnabled"
fi
/usr/lib64/openjdk-8/bin/java $SBT_OPTS -jar /usr/share/sbt/sbt.jar "$@"
