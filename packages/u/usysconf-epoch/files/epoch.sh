#!/usr/bin/bash
set -euo pipefail

# Temp: Exit if I_UNDERSTAND_THAT_THIS_SCRIPT_CAN_BREAK_MY_SYSTEM is not set
# This will be removed once we are ready to enable this by default
if [ -z "${I_UNDERSTAND_THAT_THIS_SCRIPT_CAN_BREAK_MY_SYSTEM+set}" ]; then
    exit 0
fi

# TODO place marker for eopkg to transition to new repo here

printf "I'm a little teapot"
