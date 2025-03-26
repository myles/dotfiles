if [ -d "~/Library/Application Support/Herd/bin" ]; then
    # Herd injected PHP binary.
    PATH="~/Library/Application Support/Herd/bin:$PATH"

    # Herd injected PHP 8.4 configuration.
    HERD_PHP_84_INI_SCAN_DIR="~/Library/Application Support/Herd/config/php/84/"
fi

export -U PATH
export -U HERD_PHP_84_INI_SCAN_DIR
