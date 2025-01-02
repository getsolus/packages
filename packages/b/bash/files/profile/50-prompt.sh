# Begin /usr/share/defaults/etc/profile.d/50-prompt.sh

# We cant use $SHELL since we need the *current* shell.
# The user may switch to a different shell than their default
# e.g. $SHELL is zsh but user switches to bash temporarily

current_shell=$(readlink /proc/$$/exe)

endchar="\$"
if [ "$UID" = "0" ]; then
    endchar="#"
elif [[ "$current_shell" =~ zsh ]]; then
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

if [[ "$current_shell" =~ bash ]]; then
    PS1="\[${FG}\]\u\[${AT}\]@\[${HCOLOR}\]\H \[${DIR}\]\w \[${FG}\]$endchar \[${reset_color}\]"
elif [[ "$current_shell" =~ zsh ]]; then
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
if [[ "$current_shell" =~ bash ]]; then
    shopt -s checkwinsize
fi

unset current_shell

# End /usr/share/defaults/etc/profile.d/50-prompt.sh
