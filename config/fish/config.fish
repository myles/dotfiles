test -e "$HOME/.local.fish"; and source ~/.local.fish

set -g fish_user_paths "/usr/local/sbin" $fish_user_paths

export GOPATH=$HOME/.go/

source ~/.config/fish/path.fish

# status --is-interactive; and test -e (which rbenv); and source (rbenv init -|psub)
