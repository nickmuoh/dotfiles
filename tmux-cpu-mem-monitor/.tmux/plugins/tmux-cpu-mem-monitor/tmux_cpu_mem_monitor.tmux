#!/usr/bin/env bash

set -euo pipefail

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

tmux_option() {
    local -r value="$(tmux show-option -gqv "$1")"
    local -r default="$2"

    if [ -n "$value" ]; then
        printf '%s\n' "$value"
    else
        printf '%s\n' "$default"
    fi
}

require_uv() {
    if ! command -v uv >/dev/null 2>&1; then
        tmux display-message "tmux-cpu-mem-monitor: uv is required but not installed."
        exit 1
    fi
}

set_status_right() {
    local -r lead_style="$(tmux_option '@cpu_mem_lead_style' '#[default]#[fg=brightblack,bg=black,nobold,noitalics,nounderscore]')"
    local -r metric_style="$(tmux_option '@cpu_mem_metric_style' '#[fg=white,bg=brightblack]')"
    local -r separator="$(tmux_option '@cpu_mem_metric_separator' '#[fg=white,bg=brightblack,nobold,noitalics,nounderscore]')"
    local -r cpu_icon="$(tmux_option '@cpu_mem_cpu_icon' '')"
    local -r mem_icon="$(tmux_option '@cpu_mem_mem_icon' '')"

    tmux set-option -gq status-right "#{prefix_highlight}${lead_style}${metric_style} ${cpu_icon} #{cpu} ${separator}${metric_style} ${mem_icon} #{mem} "
}

update_placeholder() {
    local -r placeholder="$1"
    local -r option="$2"
    local -r script="$3"
    local -r option_value="$(tmux show-option -gqv "$option")"

    if [[ "$option_value" != *"#{$placeholder"* ]]; then
        return
    fi

    local -r flags="$(printf '%s' "$option_value" | awk -F "#{$placeholder" '{print $2}' | sed 's/}.*//')"
    local -r token="#{${placeholder}${flags}}"
    local -r command="#(cd \"$CURRENT_DIR\" && uv run --project \"$CURRENT_DIR\" --quiet python \"$CURRENT_DIR/src/$script\"$flags)"
    local -r escaped_command="${command//&/\\&}"
    local -r new_option_value="${option_value//$token/$escaped_command}"

    tmux set-option -gq "$option" "$new_option_value"
}

main() {
    require_uv
    set_status_right

    local option
    for option in "status-right" "status-left" "status-format[0]" "status-format[1]"; do
        update_placeholder "cpu" "$option" "cpu.py"
        update_placeholder "mem" "$option" "mem.py"
        update_placeholder "disk" "$option" "disk.py"
        update_placeholder "battery" "$option" "battery.py"
    done
}

main
