# ensure dotfiles bin directory is loaded first
PATH="$HOME/.bin:$HOME/.bin-local:$HOME/.local/bin:/usr/local/sbin:$PATH"

# mkdir .git/safe in the root of repositories you trust
PATH=".git/safe/../../bin:$PATH"

export -U PATH
