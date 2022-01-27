# My `~/.dotfiles`

These are config files to set up a system the way I like it.

## Requirements

-   [rcm](https://github.com/thoughtbot/rcm) - used to manage my dotfiles.
-   [oh-my-zsh](https://ohmyz.sh/) - used to configure my zsh shell.

## Usage

Ensure you are using zsh:

	chsh -s $(which zsh)

Clone the `dotfiles` repository to your local disk:

	git clone git://github.com/myles/dotfiles ~/.dotfiles

Then run `rcup` to link all the dotfiles:

	env RCRC=$HOME/.dotfiles/rcrc rcup
