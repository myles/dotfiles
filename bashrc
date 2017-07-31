# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

source $HOME/.shell/aliases
source $HOME/.shell/functions
source $HOME/.shell/variables
source $HOME/.shell/host_specific
source $HOME/.shell/prompt
# source $HOME/.shell/completions

# Add RVM to PATH for scripting. Make sure this is the last PATH variable change.
export PATH="$PATH:$HOME/.rvm/bin"
