# tmux safety

Never run `tmux kill-server` from inside a tmux session. Reload configuration with:

```sh
tmux source-file ~/.tmux.conf
```

`$TMUX` is non-empty inside a running session.
