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

  if [[ -n "${BAMF_DESKTOP_FILE_HINT+x}" ]] || [[ -n "${GIO_LAUNCHED_DESKTOP_FILE+x}" ]]
  then
  # Ensure the notify-send meets the freedesktop standards
  # https://specifications.freedesktop.org/notification-spec/latest/
  # Keep it short and test on all DEs
  # Also, we can't use any HTML tags, they are only optionally supported
      notify-send \
          --app-name Snap \
          --urgency critical \
          --icon dialog-warning \
          "Snap has ${CONFINEMENT} confinement" \
          "See ${URL}"
  else
      echo -e "${YELLOW}WARNING:${NC} snap is running with ${CONFINEMENT} confinement." \
        "See ${URL} for details."
  fi
fi

exec -a "$0" "${SNAP}" "$@"
