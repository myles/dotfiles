export PYENV_ROOT="$HOME/.pyenv"

if [ -d "$PYENV_ROOT/bin" ]; then
    PATH="$PYENV_ROOT/bin:$PATH"
fi

if _have pyenv; then
    eval "$(pyenv init -)"
fi

export -U PATH
