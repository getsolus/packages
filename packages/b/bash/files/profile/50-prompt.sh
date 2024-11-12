# Begin /usr/share/defaults/etc/profile.d/50-prompt.sh

# If not running interactively, don't do anything
[ -t 0 ] || return 0

# We cant use $SHELL since we need the *current* shell.
# The user may switch to a different shell than their default
# e.g. $SHELL is zsh but user switches to bash temporarily
endchar="\$"
if [ "$UID" = "0" ]; then
    endchar="#"
elif [ -n "$ZSH_VERSION" ]; then
    endchar='%'
fi

# Prefer tput to ANSI codes since they work with bash and zsh
# and are much easier to read
grey=$(tput setaf 245)
pink=$(tput setaf 206)
cyan=$(tput setaf 81)
reset_color=$(tput sgr0)

FG=$cyan
DIR=$grey
AT=$grey
HCOLOR=$pink

# bash and zsh handle prompt setup and character escaping differently

if [ -n "$BASH_VERSION" ]; then
    PS1="\[${FG}\]\u\[${AT}\]@\[${HCOLOR}\]\H \[${DIR}\]\w \[${FG}\]$endchar \[${reset_color}\]"
elif [ -n "$ZSH_VERSION" ]; then
    PS1="%{${FG}%}%n%{${AT}%}@%{${HCOLOR}%}%m %{${DIR}%}%1~ %{${FG}%}$endchar# ${reset_color}"
fi

unset FG
unset BG
unset AT
unset HCOLOR
unset grey
unset pink
unset cyan
unset reset_color
unset endchar

# shopt is bash only
if [ -n "$BASH_VERSION" ]; then
    shopt -s checkwinsize
fi

# End /usr/share/defaults/etc/profile.d/50-prompt.sh
