#/bin/bash
# Install oh-my-zsh if it hasn't been installed already.

DIRECTORY="$HOME/.oh-my-zsh"

if [ ! -d "$DIRECTORY" ]; then
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
fi
