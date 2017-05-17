test -d "$HOME/.bin";         and set PATH "$HOME/.bin" $PATH
test -d "$HOME/.bin-local";   and set PATH "$HOME/.bin-local" $PATH
test -d "$HOME/.bin-private"; and set PATH "$HOME/.bin-private" $PATH

test -d "$GOPATH/bin";        and set PATH "$GOPATH/bin" $PATH

test -d "/usr/local/sbin";    and set PATH "/usr/local/sbin" $PATH
test -d "/usr/local/bin";     and set PATH "/usr/local/bin" $PATH
