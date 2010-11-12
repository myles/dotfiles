if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

# Source local additions
if [ -f ~/.bash_local ]; then
    . ~/.bash_local
fi

if [ -f `brew --prefix`/etc/autojump ]; then
    . `brew --prefix`/etc/autojump
fi
