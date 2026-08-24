HERD_ROOT="$HOME/Library/Application Support/Herd"

if [ -d "$HERD_ROOT/bin" ]; then
    # Herd injected PHP binary.
    PATH="$HERD_ROOT/bin:$PATH"

    # Herd injected PHP 8.4 configuration.
    HERD_PHP_84_INI_SCAN_DIR="$HERD_ROOT/config/php/84/"

    export -U HERD_PHP_84_INI_SCAN_DIR
fi

unset HERD_ROOT

export -U PATH
