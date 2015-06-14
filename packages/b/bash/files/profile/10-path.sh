# Begin /etc/profile.d/10-path.sh

if [ "$EUID" -eq 0 ]; then
  export PATH="/sbin:/bin:/usr/sbin:/usr/bin"
  if [ -d "/usr/local/sbin" ]; then
    export PATH="$PATH:/usr/local/sbin"
  fi
else
  export PATH="/bin:/usr/bin"
fi

if [ -d "/usr/local/bin" ]; then
  export PATH="$PATH:/usr/local/bin"
fi

if [ -d "$HOME/bin" ]; then
  export PATH="$HOME/bin:$PATH"
fi

# End /etc/profile.d/10-path.sh
