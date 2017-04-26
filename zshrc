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
