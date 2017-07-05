#!/bin/bash
PIM=`cat CMakeLists.txt | grep set | grep -E "PIM_VERSION|KDEPIM_RUNTIME_VERSION_NUMBER" | head -n 1 | sed 's/")//' | sed 's/.*"//g'`
PIMNEW=`echo ${PIM}  | sed 's/[0123]$/0/'`
sed -i "s:"${PIM}":"${PIMNEW}":" CMakeLists.txt
