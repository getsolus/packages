# Begin /usr/share/defaults/etc/profile.d/50-prompt.sh

endchar="\$"
if [ "$UID" = "0" ]; then
    endchar="#"
fi

FG="\[\033[38;5;111m\]"
BG="\[\033[38;5;168m\]"
AT="\[\033[38;5;235m\]"
HCOLOR="\[\033[38;5;61m\]"

PS1="${FG}\u${AT}@${HCOLOR}\H ${BG}\w ${FG}$endchar \[\e[0m\]"

unset FG
unset BG
unset AT
unset HCOLOR
shopt -s checkwinsize

# End /usr/share/defaults/etc/profile.d/50-prompt.sh
