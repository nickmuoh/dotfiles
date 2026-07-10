
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
