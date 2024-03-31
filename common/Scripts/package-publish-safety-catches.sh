#!/usr/bin/env bash
set -euo pipefail

check_script="$(dirname "$0")/../CI/package_checks.py"
check_args=(--base=origin/main --fail-on-warnings --results-only)

if python3 "${check_script}" "${check_args[@]}"
then
  exit 0
fi

echo "Package checks failed. Press 'y' to continue, or any other key to abort."
read -rp "Continue anyway? [yN] " prompt

if [[ $prompt = "y" ]]
then
  exit 0
else
  exit 1
fi
