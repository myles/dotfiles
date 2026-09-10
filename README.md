# My `~/.dotfiles`

These are config files to set up a system the way I like it.

## Requirements

-   [rcm](https://github.com/thoughtbot/rcm) - used to manage my dotfiles.
-   [oh-my-zsh](https://ohmyz.sh/) - used to configure my zsh shell.
-   [pre-commit](https://pre-commit.com/) - keeps credentials, private
    hosts and work config out of this public repo.

## Usage

Ensure you are using zsh:

	chsh -s $(which zsh)

Clone the `dotfiles` repository to your local disk:

	git clone git://github.com/myles/dotfiles ~/.dotfiles

Then run `rcup` to link all the dotfiles:

	env RCRC=$HOME/.dotfiles/rcrc rcup

`rcup` also installs the commit guards into `.git/hooks`. They need a denylist
of strings that must never be published, which lives outside this repo:

	mkdir -m 700 -p ~/.dotfiles-private
	$EDITOR ~/.dotfiles-private/.pre-commit-denylist.txt

Without it every commit is refused, on purpose.
