# Begin /etc/profile.d/50-prompt.sh

endchar="\$"
if [ "$UID" = "0" ]; then
    endchar="#"
fi

export FG="\033[38;5;111m"
export BG="\033[38;5;168m"
export AT="\033[38;5;235m"
export HCOLOR="\033[38;5;61m"

export PS1="${FG}\u${AT}@${HCOLOR}\H ${BG}\w 
${FG}$endchar \[\e[0;0m\]"
if [ "${TERM:0:5}" = "xterm" ]; then
  export PS1="\[\e]2;\u@\H :: \w\a\]$PS1"
fi

shopt -s checkwinsize

# End /etc/profile.d/50-prompt.sh
