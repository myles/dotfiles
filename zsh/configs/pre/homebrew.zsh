HOMEBREW_ROOT=""

if [ -d "/opt/homebrew" ]; then
    HOMEBREW_ROOT="/opt/homebrew"
    PATH="$HOMEBREW_ROOT/bin:$PATH"
elif [ -d "/usr/local/Homebrew" ]; then
    HOMEBREW_ROOT="/usr/local"
    PATH="$HOMEBREW_ROOT/Homebrew/bin:$HOMEBREW_ROOT/bin:$PATH"
else
    HOMEBREW_ROOT=""
fi

HOMEBREW_ZSH_SITE_FUNCTIONS="$HOMEBREW_ROOT/share/zsh/site-functions"

if [ -d "$HOMEBREW_ZSH_SITE_FUNCTIONS" ]; then
    for site_function in "$HOMEBREW_ZSH_SITE_FUNCTIONS"*(N-.); do
        . $site_function
    done
fi

export -U HOMEBREW_ROOT
export -U PATH
