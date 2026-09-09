if _have rbenv; then
    # --no-rehash: regenerating the shims costs ~0.2s on every shell
    # start and `rbenv install`/`gem install` rehash on their own. The
    # snippet is cached because generating it costs another ~0.25s.
    _eval_cached rbenv rbenv init - --no-rehash zsh
fi
