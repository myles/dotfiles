export PYENV_ROOT="$HOME/.pyenv"

if [ -d "$PYENV_ROOT/bin" ]; then
    PATH="$PYENV_ROOT/bin:$PATH"
fi

if _have pyenv; then
    # --no-rehash: regenerating the shims costs ~0.3s on every shell
    # start and `pyenv install` rehashes on its own. The snippet is
    # cached because generating it costs another ~0.2s.
    _eval_cached pyenv pyenv init - --no-rehash zsh
fi

export -U PATH
