
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
#
alias claude-usage='gh gist view 321b12b9e46ed872f03354609536f8aa --raw | uv run -'

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
