HOMEBREW_ROOT=""

if [ -d "/opt/homebrew" ]; then
    HOMEBREW_ROOT="/opt/homebrew"
    PATH="$HOMEBREW_ROOT/bin:$PATH"
elif [ -d "/usr/local/Homebrew" ]; then
    HOMEBREW_ROOT="/usr/local"
    PATH="HOMEBREW_ROOT/Homebrew/bin:$HOMEBREW_ROOT/bin:$PATH"
else
    HOMEBREW_ROOT=""
fi

export -U HOMEBREW_ROOT
export -U PATH
