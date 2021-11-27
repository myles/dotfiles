test -e "$HOME/.local.fish"; and source ~/.local.fish

test -e "/usr/local/sbin"; and set -g fish_user_paths "/usr/local/sbin" $fish_user_paths

source ~/.config/fish/path.fish
source ~/.config/fish/gnupg.fish

test -e "/usr/local/miniconda3/etc/fish/conf.d/conda.fish"; and source /usr/local/miniconda3/etc/fish/conf.d/conda.fish

function next_version
  bumpversion --dry-run --list $argv | grep "new_version=" | sed s,"^.*=",,
end

function up
  ping -c 1 8.8.8.8
end

function battery
  pmset -g batt | egrep "([0-9]+\%).*" -o --colour=auto | cut -f1 -d';'
  pmset -g batt | egrep "([0-9]+\%).*" -o --colour=auto | cut -f3 -d';'
end

function cpu
  sysctl -n machdep.cpu.brand_string
end

function lock
  /System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend
end

export GOPATH=$HOME/.go/

eval (python3 -m virtualfish)

status --is-interactive; and test -e (which rbenv); and source (rbenv init -|psub)

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/usr/local/google-cloud-sdk/path.fish.inc' ]; if type source > /dev/null; source '/usr/local/google-cloud-sdk/path.fish.inc'; else; . '/usr/local/google-cloud-sdk/path.fish.inc'; end; end

test -e {$HOME}/.iterm2_shell_integration.fish ; and source {$HOME}/.iterm2_shell_integration.fish


# The next line updates PATH for Netlify's Git Credential Helper.
test -f '/Users/myles/Library/Preferences/netlify/helper/path.fish.inc' && source '/Users/myles/Library/Preferences/netlify/helper/path.fish.inc'