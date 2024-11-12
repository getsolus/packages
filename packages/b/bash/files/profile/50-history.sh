# Begin /usr/share/defaults/etc/profile.d/50-history.sh

# Append to history file on exit instead of overwrite (parallel terminals)
# shopt is bash only
if [ -n "$BASH_VERSION" ]; then
    shopt -s histappend
fi

export HISTSIZE=1500
export HISTIGNORE="&:[bf]g:exit"
# ignoredups: Do not add to history the same line executed consecutively
# erasedups: All previous saved entries of line will be removed on write
export HISTCONTROL=ignoredups:erasedups

# End /usr/share/defaults/etc/profile.d/50-history.sh
