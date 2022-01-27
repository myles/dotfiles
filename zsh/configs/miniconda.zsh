export CONDA_PATH="/usr/local/miniconda3"

__conda_setup="$(CONDA_REPORT_ERRORS=false '$CONDA_PATH' shell.bash hook 2> /dev/null)"
if [ $? -eq 0 ]; then
    \eval "$__conda_setup"
else
    if [ -f "$CONDA_PATH/etc/profile.d/conda.sh" ]; then
        . "$CONDA_PATH/etc/profile.d/conda.sh"
        CONDA_CHANGEPS1=false conda activate base
    else
        \export PATH="$CONDA_PATH/bin:$PATH"
    fi
fi
unset __conda_setup
