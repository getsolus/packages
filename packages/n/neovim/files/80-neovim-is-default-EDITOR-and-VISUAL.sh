# Ensure there is a default editor should a user remove all other editors.
export EDITOR="/usr/bin/nvim"

if [[ -f "/usr/bin/nvim-qt" ]]; then
  export VISUAL="/usr/bin/nvim-qt"
else
  export VISUAL="/usr/bin/nvim"
fi
