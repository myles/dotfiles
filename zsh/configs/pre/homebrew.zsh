HOMEBREW_ROOT=""
HOMEBREW_BREW_FILE=""

# Resolve brew via its canonical symlink rather than whatever `brew` PATH
# happens to point at. Homebrew derives its prefix from the location of the
# binary that was invoked, so running the copy inside <prefix>/Homebrew/bin
# reports the internal repo as the prefix — and since PATH is inherited, one
# bad entry poisons HOMEBREW_ROOT for every nested shell.
for _brew_candidate in \
    /opt/homebrew/bin/brew \
    /usr/local/bin/brew \
    "$(command -v brew 2> /dev/null)"
do
    if [ -x "$_brew_candidate" ]; then
        HOMEBREW_BREW_FILE="$_brew_candidate"
        break
    fi
done
unset _brew_candidate

if [ -n "$HOMEBREW_BREW_FILE" ]
then
    HOMEBREW_ROOT="$("$HOMEBREW_BREW_FILE" --prefix)"
    PATH="$HOMEBREW_ROOT/bin:$PATH"

    if [ -d "$HOMEBREW_ROOT/sbin" ]; then
        PATH="$HOMEBREW_ROOT/sbin:$PATH"
    fi

    # compinit itself runs once, inside oh-my-zsh — this only has to land on
    # FPATH before that happens.
    if [ -d "$HOMEBREW_ROOT/share/zsh/site-functions" ]; then
        FPATH="$HOMEBREW_ROOT/share/zsh/site-functions:$FPATH"
    fi
fi

export -U HOMEBREW_ROOT
export -U HOMEBREW_BREW_FILE
export -U PATH
export -U FPATH
