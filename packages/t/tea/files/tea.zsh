#compdef _tea tea


_tea() {
    local curcontext="$curcontext" state state_descr line="$line"
    local ret=1
    typeset -A opt_args

    _arguments -C '*::command:->command' ':options:->options'

    list=(${(f)"$(_CLI_ZSH_AUTOCOMPLETE_HACK=1 tea $line --generate-bash-completion)"})

    _describe -t tea-subcommands 'tea subcommands' list && ret=0

    return ret
}

_tea "$@"
