##
## Initialises starship prompt for interactive shells
## Removing starship package will also remove this initialisation
##

# Check for interactive shell the POSIX sh way
[ -t 0 ] || return 0

# The linux console terminal emulator can't show the default starship prompt...
case "$TERM" in
    "linux") return 0;;
esac

# For bash
[ -n "$BASH_VERSION" ]  && eval "$(starship init bash)"

# For zsh
[ -n "$ZSH_VERSION" ] && eval "$(starship init zsh)"

# For fish
[ -n "$FISH_VERSION" ] && eval "$(starship init fish)"
