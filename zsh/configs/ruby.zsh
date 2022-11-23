RUBY_VERSION="2.7"
HONEBREW_RUBY_ROOT="$HOMEBREW_ROOT/opt/ruby@$RUBY_VERSION"

if [ -d "$HONEBREW_RUBY_ROOT" ]; then
    PATH="$HONEBREW_RUBY_ROOT/bin:$PATH"
fi

if [ -d "/usr/local/lib/ruby/gems/$RUBY_VERSION.0" ]; then
    PATH="/usr/local/lib/ruby/gems/$RUBY_VERSION.0/bin:$PATH"
fi

export -U PATH
