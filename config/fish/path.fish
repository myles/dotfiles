test -d "$HOME/.bin";         and set PATH "$HOME/.bin" $PATH
test -d "$HOME/.bin-local";   and set PATH "$HOME/.bin-local" $PATH
test -d "$HOME/.bin-private"; and set PATH "$HOME/.bin-private" $PATH

test -d "$GOPATH/bin";        and set PATH "$GOPATH/bin" $PATH

test -d "$HOME/.rbenv/bin";   and set PATH "$HOME/.rbenv/bin" $PATH
test -d "$HOME/.rbenv/shims"; and set PATH "$HOME/.rbenv/shims" $PATH

test -d "/usr/local/sbin";    and set PATH "/usr/local/sbin" $PATH
test -d "/usr/local/bin";     and set PATH "/usr/local/bin" $PATH

set -g fish_user_paths "/usr/local/opt/gettext/bin" $fish_user_paths
