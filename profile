# if running bash
if [ -n "$BASH_VERSION" ]; then
    . "$HOME/.bash_profile"
fi

# if running zsh
if [ -n "$$ZSH_VERSION" ]; then
    . "$HOME/.zshrc"
fi
