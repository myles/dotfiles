. ~/.shell/aliases
. ~/.shell/completions
. ~/.shell/functions
. ~/.shell/variables
. ~/.shell/host_specific

# Run on new shell
if [ `which fortune` ]; then
    echo ""
    fortune
    echo ""
fi