# Ensure there is a default editor should a user remove all other editors.
export EDITOR="/usr/bin/vim"

if [[ -x "/usr/bin/gvim" ]]; then
  export VISUAL="/usr/bin/gvim"
else
  export VISUAL="${EDITOR}"
fi

