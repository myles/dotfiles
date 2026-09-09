# Cache the shell snippet an `init` subcommand prints, and source the cache
# instead of re-running it. `eval "$(tool init zsh)"` spawns a subshell on
# every prompt (0.1-0.3s each here) to regenerate output that only changes
# when the tool itself does:
#
#     _eval_cached pyenv pyenv init - --no-rehash zsh
#
# The cache is rebuilt whenever the tool's binary is newer than it, so an
# upgrade picks itself up on the next shell.

ZSH_EVAL_CACHE_DIR="${ZSH_EVAL_CACHE_DIR:-$HOME/.cache/zsh-eval-cache}"

function _eval_cached() {
    local name="$1"
    shift

    local cache="$ZSH_EVAL_CACHE_DIR/$name.zsh"
    local binary

    # `whence -p` skips the shell function `init` installs, so re-sourcing
    # ~/.zshrc still compares against the real binary.
    binary="$(whence -p "$1")" || return 1

    if [[ ! -s "$cache" || "$binary" -nt "$cache" ]]; then
        mkdir -p "$ZSH_EVAL_CACHE_DIR"

        if ! "$@" > "$cache"; then
            rm -f "$cache"
            print -u2 "_eval_cached: $name init failed"
            return 1
        fi
    fi

    source "$cache"
}
