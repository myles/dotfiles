# oh-my-zsh has already run compinit (with its own 20h dump cache) by the time
# this loads, so all that is left is undoing a conflict: zsh bundles an mtools
# completion for `mcd`, which shadows our own mcd function.
compdef -d mcd
