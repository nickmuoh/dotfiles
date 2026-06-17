# Setup fzf
# ---------
if [[ ! "$PATH" == */home/nmuoh/.fzf/bin* ]]; then
  PATH="${PATH:+${PATH}:}/home/nmuoh/.fzf/bin"
fi

eval "$(fzf --bash)"
