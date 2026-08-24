export NVM_DIR="$HOME/.nvm"

NVM_ROOT="$HOMEBREW_ROOT/opt/nvm"

if [ -s "$NVM_ROOT/nvm.sh" ]; then
    . "$NVM_ROOT/nvm.sh"

    if [ -s "$NVM_ROOT/etc/bash_completion.d/nvm" ]; then
        . "$NVM_ROOT/etc/bash_completion.d/nvm"
    fi

    # Switch node versions on `cd` whenever the directory carries an .nvmrc.
    load-nvmrc() {
        local node_version nvmrc_path nvmrc_node_version

        node_version="$(nvm version)"
        nvmrc_path="$(nvm_find_nvmrc)"

        if [ -n "$nvmrc_path" ]; then
            nvmrc_node_version="$(nvm version "$(cat "${nvmrc_path}")")"

            if [ "$nvmrc_node_version" = "N/A" ]; then
                nvm install
            elif [ "$nvmrc_node_version" != "$node_version" ]; then
                nvm use
            fi
        elif [ "$node_version" != "$(nvm version default)" ]; then
            echo "Reverting to nvm default version"
            nvm use default
        fi
    }

    autoload -U add-zsh-hook
    add-zsh-hook chpwd load-nvmrc
    load-nvmrc
fi

unset NVM_ROOT
