# Begin /usr/share/defaults/etc/profile.d/10-path.sh

if [ -z ${PATH+set} ]; then

  NEW_PATH="/usr/sbin:/usr/bin"
  if [ -d "/usr/local/sbin" ]; then
    NEW_PATH="$NEW_PATH:/usr/local/sbin"
  fi

  if [ -d "/usr/local/bin" ]; then
    NEW_PATH="$NEW_PATH:/usr/local/bin"
  fi

  if [ -d "$HOME/bin" ]; then
    NEW_PATH="$HOME/bin:$NEW_PATH"
  fi

  if [ -d "$HOME/.local/bin" ]; then
    NEW_PATH="$HOME/.local/bin:$NEW_PATH"
  fi

  export PATH="$NEW_PATH"
fi

# End /usr/share/defaults/etc/profile.d/10-path.sh
