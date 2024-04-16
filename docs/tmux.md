## Tmux

See: [features](https://github.com/gpakosz/.tmux?tab=readme-ov-file#features).

**Shortcut Key**:

Remapped key to `ctrl + a`  (default: `ctrl + b`)

**Sessions**:

- New session: `:new<CR>`
- List sessions: `s`
- Name session: `$`
- List sessions: `tmux ls`
- Kill session: `tmux kill-session -t myname`
- Attach to named: `tmux a -t myname`
- Start new with session name: `tmux new -s myname`
- Kill all sessions: `tmux ls | grep : | cut -d. -f1 | awk '{print substr($1, 0, length($1)-1)}' | xargs kill`
- Exit sessions: `tmux kill-server`

**Windows**:

- Create window: `c`
- List windows: `w`
- Next window: `n`
- Previous window: `p`
- Find window: `f`
- Name window: `,`
- Kill window: `&`

**Panes**:

- Vertical split: `-`
- Horizontal split: `_`
- Swap panes: `o`
- Show pane numbers: `q`
- Kill pane: `x`
- Break pane into window (e.g. to select text by mouse to copy): `+`
- Restore pane from window: `-`
- Toggle between layouts: `⍽`
- Show pane numbers, when the numbers show up type the key to go to that pane: `q`
- Move the current pane left: `{`
- Move the current pane right: `}`
- Toggle pane zoom: `z`

**Misc**:

- Detach: `d`
- Big clock: `t`
- List shortcuts: `?`
- Prompt: `:`
- Reload settings: `r`
