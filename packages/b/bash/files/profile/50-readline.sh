# Begin /usr/share/defaults/etc/profile.d/50-readline.sh

if [ -z "$INPUTRC" ]; then
  if [ -f "$HOME/.inputrc" ]; then
    export INPUTRC="$HOME/.inputrc"
  else
    if [ -f "/etc/inputrc" ]; then
      export INPUTRC="/etc/inputrc"
    fi
  fi
fi

# End /usr/share/defaults/etc/profile.d/50-readline.sh
