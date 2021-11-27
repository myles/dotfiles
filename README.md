# Myles Braithwaite's Dot Files

These are config files to set up a system the way I like it.


## Installation

First install `rcm`:

**Debian**:

	wget https://thoughtbot.github.io/rcm/debs/rcm_1.2.3-1_all.deb
	sudo dpkg -i rcm_1.2.3-1_all.deb

**OS X**:

	brew tap thoughtbot/formulae
	brew install rcm

**Ubuntu**:

	sudo add-apt-repository ppa:martin-frost/thoughtbot-rcm
	sudo apt-get update
	sudo apt-get install rcm

**Elsewhere**:

	wget https://thoughtbot.github.io/rcm/dist/rcm-1.2.3.tar.gz && \
	tar -xvf rcm-1.2.3.tar.gz && \
	cd rcm-1.2.3 && \
	./configure && \
	make && \
	make install

Next clone the `dotfiles` repo to your local disk:

	git clone git://github.com/myles/dotfiles ~/.dotfiles

Then run `rcup` to link all the dotfiles:

	rcup
