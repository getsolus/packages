#!/bin/bash
if [[ -z "${SBT_OPTS}" ]]; then
  SBT_OPTS="-Xms512M -Xmx1536M -Xss1M -XX:+CMSClassUnloadingEnabled"
fi
java $SBT_OPTS -jar /usr/share/sbt/sbt-launch.jar "$@"
