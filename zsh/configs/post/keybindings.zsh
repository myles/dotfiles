# This lives in `post` deliberately: oh-my-zsh forces `bindkey -e` and fzf
# installs its widgets, so anything set before them gets silently discarded.

# give us access to ^Q
stty -ixon

# vi mode
bindkey -v
bindkey "^F" vi-cmd-mode

# handy keybindings
bindkey "^A" beginning-of-line
bindkey "^E" end-of-line
bindkey "^K" kill-line
bindkey "^P" history-search-backward
bindkey "^Y" accept-and-hold
bindkey "^N" insert-last-word
bindkey "^Q" push-line-or-edit

# ^R (history) and ^T (file picker) are left to fzf, which binds them into the
# vi keymaps as well as emacs, so `bindkey -v` above keeps them. Its ^I
# completion binding only lands in whichever keymap was current at load time,
# so that one does need re-applying.
if (( $+widgets[fzf-completion] )); then
    bindkey "^I" fzf-completion
fi
