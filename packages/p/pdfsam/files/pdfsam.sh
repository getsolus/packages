#!/bin/sh

if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME=/usr/lib64/openjdk-21
fi

exec "$JAVA_HOME/bin/java" --enable-preview \
  --module-path "/usr/share/pdfsam/lib" \
  --module org.pdfsam.basic/org.pdfsam.basic.App \
  -Xmx512M \
  -splash:/usr/share/pdfsam/splash.png \
  -Dapp.name="pdfsam-basic" \
  -Dapp.pid="$$" \
  -Dapp.home=/usr/share/pdfsam \
  -Dbasedir=/usr/share/pdfsam \
  -Dprism.lcdtext=false \
  "$@"
