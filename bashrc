# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

source $HOME/.shell/aliases
source $HOME/.shell/completions
source $HOME/.shell/functions
source $HOME/.shell/variables
source $HOME/.shell/host_specific
source $HOME/.shell/prompt
