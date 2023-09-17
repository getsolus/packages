# Ensure there is a default editor should a user remove all other editors.
set -gx EDITOR /usr/bin/micro
set -gx VISUAL $EDITOR
