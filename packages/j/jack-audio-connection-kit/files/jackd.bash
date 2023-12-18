#-*- mode: shell-script;-*-
# Inputs:
#   $1 -- name of the command whose arguments are being completed
#   $2 -- word being completed
#   $3 -- word preceding the word being completed
#   $COMP_LINE  -- current command line
#   $COMP_PONT  -- cursor position
#   $COMP_WORDS -- array containing individual words in the current
#                  command line
#   $COMP_CWORD -- index into ${COMP_WORDS} of the word containing the
#                  current cursor position
# Output:
#   COMPREPLY array variable contains possible completions

# Syntax:
#   jack_connect <src_port> <dst_port>
#   jack_disconnect <src_port> <dst_port>
#   jackd [options] -d backend [backend-parameters]
#   jackstart [options] -d backend [backend-parameters]

# Bugs/Todo:
#   jack_{dis,}connect should support for spaces in port names
#   restrict jack_disconnect completions to existing connections

# Bugreports: Paul Brossier <piem@altern.org>

have jack_connect &&
_jack_lsp_type() {
	jack_lsp -p | grep -B1 $1 \
		| grep -v 'properties.*,$' | grep -v ^-- \
		| sed 's/\([\/ :]\)/\\\1/g'
#		| sed 's/\([\\: ]\)/\\\1/g'
#		| sed 's/\(.*\)/"\1"/g'
}

have jackd &&
_jackd_driver_help() {
	jackd -d $1 --help 2> /dev/null | grep - \
		| sed 's/-\(.*\), --\([^\ .]*\) *\(.*\)/-\1 --\2/'
}

have jack_connect &&
_jack_connections() {
	local cur prev output IFS=$'\n'

	COMPREPLY=()
	cur=${COMP_WORDS[COMP_CWORD]}
	prev=${COMP_WORDS[COMP_CWORD-1]}

	# check if this is the first argument
	if [[ "$1" == "$prev" ]]; then
		COMPREPLY=( $( compgen -W "$(_jack_lsp_type output)" -- $cur ) )
	else
		COMPREPLY=( $( compgen -W "$(_jack_lsp_type  input)" -- $cur ) )
	fi

	return 0
}

have jackd &&
_jackd()
{
	local cur prev special

	COMPREPLY=()
	cur=${COMP_WORDS[COMP_CWORD]}
	prev=${COMP_WORDS[COMP_CWORD-1]}

	# check if backend was specified
	for (( i=0; i < ${#COMP_WORDS[@]}-1; i++ )); do
		if [[ ${COMP_WORDS[i]} == @(alsa|dummy|oss|coreaudio|portaudio) ]]; then
			special=${COMP_WORDS[i]}
		fi
	done

	# list backends
	if [[ "$prev" == -d || "$prev" == --driver ]]; then
		COMPREPLY=( $( compgen -W 'alsa dummy oss coreaudio portaudio' -- $cur ) )
	# list backend specific options
	elif [ -n "$special" ]; then
		COMPREPLY=( $( compgen -W '`_jackd_driver_help $special` --help' -- $cur ) )
	# list common options
	else
		COMPREPLY=( $( compgen -W '--help -h \
			--driver -d \
			--realtime -R \
			--realtime-priority -P \
			--name -n \
			--no-mlock -m \
			--unlock -u \
			--timeout -t \
			--port-max -p \
			--verbose -v \
			--silent -s \
			--version -V' -- $cur ) )
	fi

	return 0
}

[ "$have" ] && complete -F _jack_connections $filenames jack_connect
[ "$have" ] && complete -F _jack_connections $filenames jack_disconnect
[ "$have" ] && complete -F _jackd $filenames jackd
[ "$have" ] && complete -F _jackd $filenames jackstart
