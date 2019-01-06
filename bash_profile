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
# added by Anaconda3 5.3.0 installer
# >>> conda init >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$(CONDA_REPORT_ERRORS=false '/anaconda3/bin/conda' shell.bash hook 2> /dev/null)"
if [ $? -eq 0 ]; then
    \eval "$__conda_setup"
else
    if [ -f "/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/anaconda3/etc/profile.d/conda.sh"
        CONDA_CHANGEPS1=false conda activate base
    else
        \export PATH="/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda init <<<
