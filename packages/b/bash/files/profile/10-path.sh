# Begin /usr/share/defaults/etc/profile.d/10-path.sh

PREFIX_PATH=
POSTFIX_PATH=

# PATH exists, only append missing stuff to it
if [[ -n "${PATH}" ]]; then

  echo "DEBUG: Starting \$PATH: ${PATH}"

  for d in "/usr/sbin" "/usr/bin" "/usr/local/sbin" "/usr/local/bin"; do
    # respect user path ordering if the element is already in $PATH
    if [[ "${PATH}" =~ "${d}" ]]; then
      :
      echo "DEBUG: Skipping ${d} as it is already in \$PATH"
    else
      POSTFIX_PATH="${POSTFIX_PATH}:${d}"
      echo "DEBUG: Added ${d} to \$POSTFIX_PATH, \$POSTFIX_PATH is now: ${POSTFIX_PATH}"
    fi
  done

  for d in "${HOME}/.local/bin" "${HOME}/bin"; do
    # respect user path ordering if the element is already in $PATH
    if [[ "${PATH}" =~ "${d}" ]]; then
      :
      echo "DEBUG: Skipping ${d} as it is already in \$PATH"
    else
      PREFIX_PATH="${d}:${PREFIX_PATH}"
      echo "DEBUG: Added ${d} to \$PREFIX_PATH, \$PREFIX_PATH is now: ${PREFIX_PATH}"
    fi
  done

  # this should adequately respect existing path definitions
  PATH="${PREFIX_PATH}${PATH}${POSTFIX_PATH}"

else
# PATH does NOT exist, build it from scratch.

  echo "DEBUG: \$PATH is empty, building a default \$PATH ..."

  DEFAULT_PATH="/usr/sbin:/usr/bin"
  if [[ -d "/usr/local/sbin" ]]; then
    DEFAULT_PATH="${DEFAULT_PATH}:/usr/local/sbin"
  fi

  if [[ -d "/usr/local/bin" ]]; then
    DEFAULT_PATH="${DEFAULT_PATH}:/usr/local/bin"
  fi

  if [[ -d "$HOME/bin" ]]; then
    DEFAULT_PATH="${HOME}/bin:${DEFAULT_PATH}"
  fi

  if [[ -d "$HOME/.local/bin" ]]; then
    DEFAULT_PATH="${HOME}/.local/bin:${DEFAULT_PATH}"
  fi

  PATH="${DEFAULT_PATH}"
fi

export PATH="${PATH}"
echo "DEBUG: \$PATH is now: ${PATH}"

# End /usr/share/defaults/etc/profile.d/10-path.sh
