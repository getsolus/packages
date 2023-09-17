# Ensure there is a default editor should a user remove all other editors.
set -gx EDITOR /usr/bin/vim

if test -e /usr/bin/gvim
  set -gx VISUAL /usr/bin/gvim
else
  set -gx VISUAL $EDITOR
end
