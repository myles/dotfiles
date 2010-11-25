if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

# Source local additions
if [ -f ~/.bash_local ]; then
    . ~/.bash_local
fi

# Source private additions
if [ -f ~/.bash_private ]; then
    . ~/.bash_private
fi