#!/usr/bin/sh
: "${VHS_NO_SANDBOX:=1}"
export VHS_NO_SANDBOX
exec /usr/share/vhs/vhs "$@"
