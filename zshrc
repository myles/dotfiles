# Make prompt prettier
autoload -U promptinit
promptinit

. ~/.shell/aliases
. ~/.shell/functions
. ~/.shell/prompt
. ~/.shell/variables
. ~/.shell/host_specific

if [ -f ~/.bash_local ]; then
    . ~/.bash_local
fi

# Add RVM to PATH for scripting. Make sure this is the last PATH variable change.
export PATH="$PATH:$HOME/.rvm/bin"

# added by travis gem
[ -f $HOME/.travis/travis.sh ] && source $HOME/.travis/travis.sh
