
#
# difftastic
#
alias difft='/snap/bin/difftastic'

#
# bat
#
alias bat='batcat'
alias bathelp='bat --plain --language=help'
help() {
  "$@" --help 2>&1 | bathelp
}

#
# batlog
#

## How to use it
# Default (newest log):
# batlog

## Single index:
# batlog 2 (opens 2nd newest)

## Range with hyphen:
# batlog 1-3 (opens 1st, 2nd, and 3rd newest)

## Multiple specific indices:
# batlog 1 4 6 (opens 1st, 4th, and 6th newest)

## Combine ranges and individual indices:
# batlog 1-3 5 (opens 1st through 3rd, plus 5th)

batlog() {
  local sed_pattern=""

  # Default to the 1st (newest) log if no argument is passed
  if [ $# -eq 0 ]; then
    sed_pattern="1p"
  else
    # Loop through arguments and convert hyphens to commas (e.g., 1-3 -> 1,3p)
    for arg in "$@"; do
      sed_pattern="${sed_pattern}${arg//-/,}p "
    done
    # Remove trailing space
    sed_pattern="${sed_pattern% }"
  fi

  # Check if logs/ directory exists
  if [ ! -d logs/ ]; then
    echo "Error: logs/ directory not found. Please create it or check your PATH."
    return 1
  fi

  # Read selected files into an array
  local files=($(ls -t logs/ | sed -n "$sed_pattern" | sed 's/^/logs\//'))

  if [ ${#files[@]} -gt 0 ]; then
    bat --theme='ansi' "${files[@]}"
  else
    echo "No matching log files found."
  fi
}

#
# GitHub Copilot
#
ghc() {
  copilot \
    --autopilot \
    --allow-tool='shell(poe sqlmesh:*)' \
    --allow-tool='shell(git:*)' \
    --deny-tool='shell(git push)' \
    --allow-url='docs.snowflake.com,sqlmesh.readthedocs.io' \
    "$@"
}

#
# Claude Usage Tracker
# Check latest version at https://github.com/SketchUp/warehouse_spa/blob/develop/scripts/claude-usage-tracker.py
# Update secret gist https://gist.github.com/nickmuoh/
#
alias claude-usage='gh gist view dad1c144f050dc62c4256e6605d3e151 --raw | uv run -'

#
# Windows Terminal
#
set_wt_title() {
  printf '\033]0;%s\007' "$*"
}

#
# Ollama Tunnel
#
ollama_tunnel() {
  local session_name="${1:-ollama}"
  local remote_host="${2:-anansi}"
  local local_port="${3:-11435}"
  local remote_port="${4:-11434}"

  set_wt_title "🦙🔗 Ollama - ${remote_host}"

  ssh -tt \
    -L "127.0.0.1:${local_port}:127.0.0.1:${remote_port}" \
    "${remote_host}" \
    "if tmux has-session -t '${session_name}' 2>/dev/null; then
       tmux attach-session -t '${session_name}'
     else
       tmux new-session -d -s '${session_name}'
       tmux send-keys -t '${session_name}' 'watch ollama ps' Enter
       tmux split-window -v -t '${session_name}' -p 95
       tmux send-keys -t '${session_name}' 'htop' Enter
       tmux split-window -v -t '${session_name}' -p 55
       tmux send-keys -t '${session_name}' 'nvtop' Enter
       tmux select-pane -t '${session_name}:0.0'
       tmux attach-session -t '${session_name}'
     fi"

  set_wt_title "WSL"
}
