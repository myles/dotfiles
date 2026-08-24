# Apple Silicon installs usually land somewhere else — override by editing this
# path if conda ever moves.
export CONDA_PATH="/usr/local/miniconda3"

if [ -x "$CONDA_PATH/bin/conda" ]; then
    if __conda_setup="$(CONDA_REPORT_ERRORS=false "$CONDA_PATH/bin/conda" shell.zsh hook 2> /dev/null)"; then
        eval "$__conda_setup"
    elif [ -f "$CONDA_PATH/etc/profile.d/conda.sh" ]; then
        . "$CONDA_PATH/etc/profile.d/conda.sh"
        CONDA_CHANGEPS1=false conda activate base
    else
        PATH="$CONDA_PATH/bin:$PATH"
    fi

    unset __conda_setup
fi

export -U PATH
