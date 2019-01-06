# if running bash
if [ -n "$BASH_VERSION" ]; then
    . "$HOME/.bash_profile"
fi

# if running zsh
if [ -n "$ZSH_VERSION" ]; then
    . "$HOME/.zshrc"
fi

# Add RVM to PATH for scripting. Make sure this is the last PATH variable change.
export PATH="$PATH:$HOME/.rvm/bin"

[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm" # Load RVM into a shell session *as a function*

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm

gam() { "/Users/myles/bin/gam/gam" "$@" ; }
