# Begin /usr/share/defaults/etc/profile.d/50-prompt.sh

endchar="\$"
if [ "$UID" = "0" ]; then
    endchar="#"
fi

FG="\[\033[38;5;081m\]"
BG="\[\033[38;5;245m\]"
AT="\[\033[38;5;245m\]"
HCOLOR="\[\033[38;5;206m\]"

PS1="${FG}\u${AT}@${HCOLOR}\H ${BG}\w ${FG}$endchar \[\e[0m\]"

unset FG
unset BG
unset AT
unset HCOLOR
if [ $SHELL != "/bin/zsh" ]; then
    shopt -s checkwinsize
fi

# End /usr/share/defaults/etc/profile.d/50-prompt.sh
