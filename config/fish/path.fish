test -d "/usr/local/miniconda3/bin"; and set -g fish_user_paths "/usr/local/miniconda3/bin" $fish_user_paths

test -d "$HOME/.bin"; and set -g fish_user_paths "$HOME/.bin" $fish_user_paths
test -d "$HOME/.bin-local"; and set -g fish_user_paths "$HOME/.bin-local" $fish_user_paths
test -d "$HOME/.bin-private"; and set -g fish_user_paths "$HOME/.bin-private" $fish_user_paths

test -d "$GOPATH/bin"; and set -g fish_user_paths "$GOPATH/bin" $fish_user_paths

test -d "$HOME/.local/bin"; and set -g fish_user_paths "$HOME/.local/bin" $fish_user_paths
test -d "$HOME/.cargo/bin"; and set -g fish_user_paths "$HOME/.cargo/bin" $fish_user_paths

test -d "$HOME/.rbenv/bin"; and set -g fish_user_paths "$HOME/.rbenv/bin" $fish_user_paths
test -d "$HOME/.rbenv/shims"; and set -g fish_user_paths "$HOME/.rbenv/shims" $fish_user_paths

test -d "/usr/local/sbin"; and set -g fish_user_paths "/usr/local/sbin" $fish_user_paths
test -d "/usr/local/bin"; and set -g fish_user_paths "/usr/local/bin" $fish_user_paths

test -d "/usr/local/opt/gettext/bin"; and set -g fish_user_paths "/usr/local/opt/gettext/bin" $fish_user_paths
