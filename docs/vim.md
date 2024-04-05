## Vim

**General**

- `ctrl + v`: Visual block mode
- `ctrl + i/o`: Transition between locations
- `ctrl + r`: Redo
- `yw`: Yank word
- `cw`: Change word
- `ce`: Change until end of word
- `cgn`: Change the next search item
- `ctrl + e/y`: Move without cursor
- `Ctrl + u / d`: Move cursor half-page up / down
- `A`: Append on the end of sentence
- `dw`: Delete word
- `d$`: Delete to end of line
- `d2w, 2dd`: Delete 2 words or 2 lines
- `U`: Return line to original state
- `r`: Rename character
- `R`: Replace many characters
- `shift+i`: After visual to edit at beginning of line
- `ctrl+g`: Show position in a file
- `10G`: Go to line 10
- `n/N`: Next/previous searched text
- `/ ?`: Search forward/backward
- `"2p`: Paste second yank
- `ctrl+d`: Vim show list of command names
- `ctrl+w`: In insert mode jump back
- `diw`: Delete word under cursor
- `viw`: Select word under cursor
- `vae`: Select all text
- `vi)`: Select inside parenthesis
- `:!dir`: Execute external command 'dir'
- `:r TEST`: Retrieve text from 'TEST' to current file
- `:r !ls`: Reads the output of the 'ls' command
- `:help w`: Help for 'w'
- `:reg`: Saved yank text

**Rename**:

- `:s/thee/the <ENTER>`: Change 'thee' to 'the'
- `:s/thee/the/g`: Globally change 'thee' to 'the'
- `:#,#s/old/new/g`: Substitute 'old' with 'new' between specific line numbers
- `:%s/old/new/g`: Substitute every occurrence of 'old' with 'new' in the whole file
- `:%s/old/new/gc`: Substitute every occurrence of 'old' with 'new' in the whole file with a prompt for each

**Record**

- `qx`: Start recording to register x
- `:%s/OldString/NewString/g`: Replace 'OldString' with 'NewString'
- `q`: Stop recording
- `@x`: Playback to see if it works correctly
- `999@x`: Repeat 999 times to complete the job

**Navigation**

- `*`: Search for word under the cursor
- `#`: Go to previous whole word under cursor
- `^`: Go to the first non-blank character of the line
- `zz`: Go to middle of the screen
- `zb`: Go to bottom of the screen
- `zt`: Go to top of the screen
- `:jumps`: See jumps

**File Management**:
- `:wnext`: Go to next file
- `:w TEST`: Save file with filename 'TEST'
- `:bd | e filename`: Close current and open another file

**Window Management**

- `ctrl+w ctrl+w`: Move between windows
- `ctrl+w+q`: Close window
- `ctrl+w+v`: Vertical split
- `CTRL+W T`: Break out current window into a new tabview
- `CTRL+W o`: Close every window in the current tabview but the current one
- `CTRL+W n`: Create a new window in the current tabview
- `CTRL+W c`: Close current window in the current tabview
- `CTRL+w >`: Incrementally increase the window to the right. Takes a parameter, e.g. `CTRL-w 20 >`
- `CTRL+w <`: Incrementally increase the window to the left. Takes a parameter, e.g. `CTRL-w 20 <`
- `CTRL+w -`: Incrementally decrease the window's height. Takes a parameter, e.g. `CTRL-w 10 -`
- `CTRL+w +`: Incrementally increase the window's height. Takes a parameter, e.g. `CTRL-w 10 +`

**VSCode**

- `gd`: Jump to definition
- `gq`: On a visual selection, reflow and wordwrap blocks of text, preserving commenting style. Great for formatting documentation comments
- `gb`: Adds another cursor on the next word
- `gh`: Equivalent to hovering your mouse over wherever the cursor is
- `gc`: Comment
- `gc2j`: Comment 2 lines down
- `af`: Visual mode command which selects increasingly large blocks of text
- `gt`: Go to next tab
- `gT`: Go to previous tab
- `gv`: Bring back selection from visual mode
- `<<`: Rtab
- `>>`: Tab

**Plugins**

- **easymotion**
  - `<leader><leader> s + char`: Search for character

- **surround**
  - `d s <existing char>`: Delete existing surround
  - `c s <existing char> <desired char>`: Change surround existing to desired
  - `y s <motion> <desired char>`: Surround something with something using motion (as in "you surround")
  - `S <desired char>`: Surround when in visual modes (surrounds full selection)

- **indent-object**
  - `<operator>ii`: This indentation level (`<operator>` can be `v` or `V`)
  - `<operator>ai`: This indentation level and the line above (think if statements in Python)
  - `<operator>aI`: This indentation level, the line above, and the line after (think if statements in C/C++/Java/etc)
