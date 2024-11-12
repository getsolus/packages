source /usr/share/defaults/etc/zsh/zprofile

# User specific zsh scripts and functions
if [ -d ~/.zshrc.d ]; then
    for rc in ~/.zshrc.d/*; do
        if [ -f "$rc" ]; then
            . "$rc"
        fi
    done
    unset rc
fi
