# Begin /usr/share/defaults/etc/profile.d/10-path.sh

export PATH="/sbin:/bin:/usr/sbin:/usr/bin"
if [ -d "/usr/local/sbin" ]; then
  export PATH="$PATH:/usr/local/sbin"
fi

if [ -d "/usr/local/bin" ]; then
  export PATH="$PATH:/usr/local/bin"
fi

if [ -d "$HOME/bin" ]; then
  export PATH="$HOME/bin:$PATH"
fi

if [ -d "$HOME/.local/bin" ]; then
  export PATH="$HOME/.local/bin:$PATH"
fi

# End /usr/share/defaults/etc/profile.d/10-path.sh
