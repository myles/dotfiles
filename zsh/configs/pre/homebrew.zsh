HOMEBREW_ROOT=""
HOMEBREW_BREW_FILE=""

if type brew &>/dev/null
then
    HOMEBREW_BREW_FILE="$(brew --prefix)/bin/brew"
elif type /opt/homebrew/bin/brew &>/dev/null
then
    HOMEBREW_BREW_FILE="/opt/homebrew/bin/brew"
elif type /usr/local/bin/brew &>/dev/null
then
    HOMEBREW_BREW_FILE="/usr/local/bin/brew"
fi

if [[ -v HOMEBREW_BREW_FILE ]]
then
    HOMEBREW_ROOT="$($HOMEBREW_BREW_FILE --prefix)"
    PATH="$HOMEBREW_ROOT/bin:$PATH"

    if [ -d "$HOMEBREW_ROOT/Homebrew/bin" ]; then
        PATH="$HOMEBREW_ROOT/Homebrew/bin:$PATH"
    fi

    if [ -d "$HOMEBREW_ROOT/share/zsh/site-functions" ]; then
        FPATH="$HOMEBREW_ROOT/share/zsh/site-functions:$FPATH"

        autoload -Uz compinit
        compinit
    fi
fi

export -U HOMEBREW_ROOT
export -U PATH
