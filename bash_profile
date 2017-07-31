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

# rbenv
if which rbenv > /dev/null; then
  eval "$(rbenv init -)";
fi

[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm" # Load RVM into a shell session *as a function*
