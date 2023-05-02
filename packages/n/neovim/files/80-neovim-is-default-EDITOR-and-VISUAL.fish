# Ensure there is a default editor should a user remove all other editors.
set -gx EDITOR /usr/bin/nvim

if test -e /usr/bin/nvim-qt
  set -gx VISUAL /usr/bin/nvim-qt
else
  set -gx VISUAL /usr/bin/nvim
end
