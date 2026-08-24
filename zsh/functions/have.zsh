# Guard for optional tooling, so a missing binary is a no-op rather than a
# "command not found" on every prompt: `_have foo && eval "$(foo init zsh)"`.

function _have() {
    command -v "$1" > /dev/null 2>&1
}
