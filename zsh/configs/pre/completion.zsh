# Completion functions have to be on FPATH before compinit runs, and compinit
# runs inside oh-my-zsh — which loads after this `pre` tier. See post/completion.zsh
# for the parts that have to happen afterwards.
fpath=(~/.zsh/completion /usr/local/share/zsh/site-functions $fpath)
