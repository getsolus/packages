#!/usr/bin/env bash
set -euo pipefail

YELLOW='\033[0;33m'
NC='\033[0m'
URL="https://help.getsol.us/docs/user/software/third-party/snap"
SNAP="/usr/lib64/snapd/snap"
CONFIG="/var/lib/snapd/solus"
CONFINEMENT="$("${SNAP}" debug confinement 2>/dev/null)"

if [[ -e "${CONFIG}" ]]
then
  # shellcheck disable=SC1090
  . "${CONFIG}"
fi

if [[ "$#" -ge 1 ]] && [[ "$1" == "hide-confinement-warning" ]]
then
  echo "This will disable warnings when snap is running without strict confinement."
  read -rp "Are you sure you want to do this [yN]? " choice
  if [[ "${choice}" = "y" ]]
  then
    echo "DISABLE_CONFINEMENT_WARNING=y" >> "${CONFIG}"
    echo "Confinement warnings disabled."
  fi

  exit 0
fi

if [[ "${CONFINEMENT}" != "strict" ]] && [[ "${DISABLE_CONFINEMENT_WARNING:-n}" != "y" ]]
  then
  if [[ -n "${BAMF_DESKTOP_FILE_HINT+x}" ]] && [[ -n "${GIO_LAUNCHED_DESKTOP_FILE+x}" ]]
  then
      notify-send \
          --app-name Snap \
          --urgency normal \
          --icon dialog-warning \
          "Snap has ${CONFINEMENT} confinement" \
          "Snaps will stop working in early January 2025." \
          "See ${URL} for details."
  else
      echo -e "${YELLOW}WARNING:${NC} snap is running with ${CONFINEMENT} confinement." \
        "Snaps will stop working in early January 2025." \
        "See ${URL} for details"
  fi
fi

exec -a "$0" "${SNAP}" "$@"
