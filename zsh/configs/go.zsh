GOPATH="$HOME/.go"
GOROOT="$(brew --prefix go)/libexec"
PATH="$PATH:${GOPATH}/bin:${GOROOT}/bin"

export -U GOPATH
export -U GOROOT
export -U PATH
