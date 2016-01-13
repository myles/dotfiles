# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

. $HOME/.shell/aliases
. $HOME/.shell/completions
. $HOME/.shell/functions
. $HOME/.shell/variables
. $HOME/.shell/host_specific
. $HOME/.shell/prompt

