if [ -f $HOME/.bashrc ]; then
    . $HOME/.bashrc
fi

# Source local additions
if [ -f $HOME/.bash_local ]; then
    . $HOME/.bash_local
fi

# Source private additions
if [ -f $HOME/.bash_private ]; then
    . $HOME/.bash_private
fi


source ~/.xsh

