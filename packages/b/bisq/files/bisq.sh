#!/bin/sh
exec /usr/lib64/openjdk-8/bin/java -Dsecurity.provider.11=org.bouncycastle.jce.provider.BouncyCastleProvider -jar /usr/share/bisq/bisq.jar "$@"

