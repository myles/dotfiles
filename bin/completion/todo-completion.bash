_todo()
{
	local cur prev opts
	COMPREPLY=()
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"
	COMMANDS="add a addto addm append app archive command del  \
			rm depri dp do help list ls listall lsa listcon  \
			lsc listfile lf listpri lsp listproj lsprj move  \
			mv prepend prep pri p replace report"
	# Add custom commands from add-ons, if installed. 
	COMMANDS="$COMMANDS $('ls' ${TODO_ACTIONS_DIR:-$HOME/.todo.actions.d}/ 2>/dev/null)"
	OPTS="-@ -@@ -+ -++ -d -f -h -p -P -PP -a -n -t -v -vv -V -x"
	if [ "${cur:0:1}" == "+" ]; then
		completions="$(t listproj)"
	elif [ "${cur:0:1}" == "@" ]; then
		completions="$(t listcon)"
	elif [ $COMP_CWORD -eq 1 ]; then
		completions="$COMMANDS $OPTS"
	else
		case "${prev}" in
			-*) completions="$COMMANDS $OPTS";;
			*)  return 0;;
		esac
	fi
	COMPREPLY=( $( compgen -W "$completions" -- $cur ))
	return 0
}
complete -F _todo todo.sh
# If you define an alias (e.g. "t") to todo.sh, you need to explicitly enable
# completion for it, too: 
complete -F _todo t
complete -F _todo todo