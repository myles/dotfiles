HOMEBREW_ROOT=""

if type /opt/homebrew/bin/brew &>/dev/null
then
    HOMEBREW_ROOT="$(/opt/homebrew/bin/brew --prefix)"
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
