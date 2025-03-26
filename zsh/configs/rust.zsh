CARGO_ROOT="$HOME/.cargo"

if [ -d "$CARGO_ROOT" ]; then
    PATH="$CARGO_ROOT/bin:$PATH"
fi

export -U PATH
