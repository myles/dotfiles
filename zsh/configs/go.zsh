GOPATH="$HOME/.go"
GOROOT="$HOMEBREW_ROOT/opt/go/libexec"

PATH="$PATH:${GOPATH}/bin"

if [ -d "$GOROOT" ]; then
    PATH="$PATH:${GOROOT}/bin"
else
    GOROOT=""
fi

export -U GOPATH
export -U GOROOT
export -U PATH
