---
name: daily-obsidian-vault-commit
description: Obsidian Vault — Daily Commit
---

# Routine: Obsidian Vault — Daily Commit

## Metadata

| Field         | Value                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------- |
| Trigger       | Daily                                                                                       |
| Purpose       | Snapshot all changes in the Obsidian vault to git on `main` with an agent-readable message. |
| Vault         | `~/mydrive/brain/Notes`                                                                     |
| Branch        | `main` (commit only — repository has no remote, nothing is pushed).                         |
| Execution env | Local checkout of the vault. No worktree, no extra tooling.                                 |

## Workflow

The routine runs the steps below **in order**. A step must succeed before the next one starts. If any step aborts, follow the _Failure handling summary_ and post the failure verdict per _Slack notification_.

All steps run from the vault root: `cd ~/mydrive/brain/Notes`.

**Sandbox:** the harness sandbox denies writes inside `.git/`, so any git command that mutates the repo (`git add`, `git commit`) will fail with `Unable to create '.git/index.lock': Operation not permitted` under default sandboxing. Run those commands with `dangerouslyDisableSandbox: true`. Read-only commands (`git symbolic-ref`, `git status`, `git diff`, `git log`) stay sandboxed.

### Step 1 — Confirm branch is `main`

The routine runs directly in the main vault checkout — no worktree, no isolation. The only precondition is the branch.

```bash
cd ~/mydrive/brain/Notes
git symbolic-ref --short HEAD   # must print: main
```

**On failure:** Stop. Do **not** auto-checkout `main` — the user may have intentionally switched branches. Report the actual branch in the routine output.

### Step 2 — Inspect changes

```bash
git status --porcelain
```

If the output is empty, print the _No-op_ block from _Routine output contract_ and exit success. Skip the remaining steps.

Otherwise continue to Step 3.

### Step 3 — Stage everything

```bash
git add -A
```

Existing `.gitignore` is the only exclusion mechanism. Do **not** filter files manually here — anything the user wanted excluded should already be in `.gitignore`. Suspect entries are surfaced in Step 6, not silently dropped.

### Step 4 — Synthesize the commit message

Read the staged diff (`git diff --cached`) and write the message. Format is intentionally plain — `git log` plus `git log --name-status` is the parsing surface, so the message body is reserved for things git cannot synthesize on its own.

If the diff is very large (>~2000 lines), truncate before reading — a runaway diff must not blow the context window. In that case use the fallback subject below.

**Subject (required, 50–72 chars total, including the prefix):**

- **Required prefix:** `[auto] ` — marks the commit as produced by this scheduled routine, so `git log` makes the human-vs-agent split obvious at a glance. This is the _only_ permitted prefix.
- After the prefix, write a natural-language summary in **content** terms — name the topics, ideas, sections, or templates that changed.
- Specifics over generics: `[auto] Expand systematic-debugging chapter; add weekly-review template` beats `[auto] Update notes`.
- **No** Conventional Commits prefix (`notes:`, `chore:`, etc.) on top of `[auto]` — those carry no signal here. The `[auto]` marker is the only prefix that matters.
- **No** date or file count in the subject — the date is already on the commit, the file list is in `git log --name-status`.

**Body (required trailer, plus optional prose):**

- Always end the body with the trailer line `Routine: daily-obsidian-vault-commit` so the source skill is recoverable from the commit alone.
- Optionally precede the trailer with 1–3 sentences of prose, but only when the diff covers multiple unrelated themes that don't fit in the subject. Describe themes in prose; do **not** list files.

Examples:

```
[auto] Expand systematic-debugging chapter; tweak weekly-review template

Routine: daily-obsidian-vault-commit
```

```
[auto] Reorganize project-management notes; add weekly-review template

Split the Areas/Projects PARA folder by lifecycle stage. New template under
Templates/weekly-review.md collects the prompts I've been using ad-hoc.

Routine: daily-obsidian-vault-commit
```

**Fallback (if synthesis fails or the diff was truncated):** use a generic subject of the form `[auto] Vault snapshot — N files changed` (where N is from `git diff --cached --stat`). Keep the `[auto]` prefix and the body trailer. Still proceed to Step 5; do not abort.

### Step 5 — Commit

Pass the message via heredoc to preserve formatting. The `[auto]` subject prefix and the `Routine:` trailer are mandatory — they are how downstream tools (and the user) tell agent commits apart from human commits.

```bash
git commit -m "$(cat <<'EOF'
[auto] <subject>

<optional prose body>

Routine: daily-obsidian-vault-commit
EOF
)"
```

If there is no prose body, the message is just the subject + a blank line + the trailer:

```bash
git commit -m "$(cat <<'EOF'
[auto] <subject>

Routine: daily-obsidian-vault-commit
EOF
)"
```

**Do not** pass `--no-verify`. **Do not** amend a prior commit. **Do not** retry with skip-hook flags if a hook fails.

**On failure (hook rejected the commit, working tree changed mid-run, etc.):** Stop. Leave the changes staged on disk. Report the failing hook (or other reason) and its output verbatim in the routine output. Post the failure verdict per _Slack notification_.

### Step 6 — Pattern observation pass

Re-read the file list captured in Step 2 and flag anything that looks like it should NOT be in git. Common offenders for an Obsidian vault:

- `.DS_Store`, `.AppleDouble`, `Thumbs.db` — OS metadata
- `.obsidian/workspace*`, `.obsidian/cache`, `.obsidian/types.json` — per-machine Obsidian UI state
- `.trash/`, `.smart-env/`, `.smart-connections/` — plugin caches
- Lock / swap / temp files: `*.swp`, `*.lock`, `*.tmp`, `*.bak`
- Large media files (> 5 MB) that probably belong in a dedicated attachments store, not in a notes repo

For each suspected offender, emit a one-line proposal in the routine output:

```
Suggest gitignoring: `.obsidian/workspace.json` (per-machine UI state, no value tracked)
Suggest gitignoring: `**/*.tmp` (temporary files leaked into the commit)
```

Do **not** auto-edit `.gitignore`. Observations are advisory and live only in the current run's output — there is no cross-run persistence by design. If the same suggestion shows up day after day, the user will act on it.

This step is non-fatal: if it errors, log the error inline and still report the routine as successful.

### Step 7 — Update knowledge graph

If Step 5 committed, refresh the vault's knowledge graph via the wrapper script at `wiki/graph/graphify.sh`. This step is **best-effort and non-fatal** — the commit has already landed, so a graph failure must not fail the routine.

**Precondition check** — run the update if **either** signal indicates pending work:

1. The just-made commit (`HEAD~1..HEAD`) touched markdown outside `wiki/graph/`, **or**
2. `wiki/graph/graphify-out/needs_update` exists — the `flag`-mode post-commit hook set this on some earlier commit (typically a manual commit made during the day) that hasn't been processed yet.

Skip only when **both** are false: this commit doesn't change markdown AND no flag is pending. Pure-attachment, pure-config, or graph-only commits with no pending flag don't change the graph corpus and would waste LLM tokens.

```bash
changed_md=$(git diff HEAD~1 HEAD --name-only -- '*.md' ':!wiki/graph/**')
flag_set=0
[ -f wiki/graph/graphify-out/needs_update ] && flag_set=1

if [ -z "$changed_md" ] && [ "$flag_set" -eq 0 ]; then
  # Report "Graph: skipped (no pending changes)" in the Success block and stop here.
  :
fi
```

Note: the flag alone doesn't tell us *what* changed (the hook sets it on every commit, content-blind), so it may occasionally trigger an `update` run that finds little real work. That's acceptable — graphify's manifest-based change detection keeps actual LLM extraction cost proportional to real markdown deltas.

**Run** (synchronous; the script writes to `wiki/graph/graphify-out/`, never to `.git/`, so it stays inside the harness sandbox):

```bash
./wiki/graph/graphify.sh update
```

The script handles its own locking (`~/.cache/graphify-vault-locks/`) and logging (`~/.cache/graphify-vault.log`). It clears `graphify-out/needs_update` on success.

**Reporting:**

- Exit 0 → `Graph: updated`
- Non-zero exit, or timeout → `Graph: failed (<short reason>)`, and include the last ~10 lines of stderr in the routine's Details block. Do **not** abort the routine.
- Precondition skipped the run → `Graph: skipped (no pending changes)`

**Flag interaction:** when this step starts, `graphify-out/needs_update` will usually be set — the `flag`-mode post-commit hook touched it after Step 5. A successful `update` clears the flag. If the update failed, the flag remains, so tomorrow's run will see it and try again — that's the intended recovery hand-off.

## Routine output contract

The routine prints exactly one terminal block at the end. Stable headings make the output easy to skim and trivial to parse.

**Success (something committed):**

```
:white_check_mark: daily-obsidian-vault-commit <YYYY-MM-DD>
Commit: <short SHA> — <subject>
Files: <added>+ <modified>~ <deleted>-
Graph: updated | skipped (no pending changes) | failed (<reason>)
Observations: <count>

<observation lines, if any — one per line, format from Step 6>
```

**No-op (clean tree):**

```
:information_source: daily-obsidian-vault-commit <YYYY-MM-DD> — nothing to commit.
```

**Failure:**

```
:x: daily-obsidian-vault-commit <YYYY-MM-DD> — <step> failed
Reason: <short reason>
Details:
<verbatim error / hook output>
```

## Slack notification (verdict only)

After the routine reaches a terminal state — success, no-op, or failure — post one short Slack DM to the routine owner so they get a passive ping without opening the routine output. The owner reads the routine's text output for everything else (commit SHA, observations, graph status, etc.); Slack carries only the verdict.

- **Destination:** Direct message to the routine owner (self-DM in the authenticated workspace) — resolve identity from session context (e.g. the `# userEmail` block) rather than hard-coding it.
- **Channel:** Slack via the `plugin:slack:slack` MCP server.
- **Auth:** If the server reports as unauthenticated, call `mcp__plugin_slack_slack__authenticate` to start the OAuth flow, then `mcp__plugin_slack_slack__complete_authentication` with the callback URL. Subsequent runs reuse the stored credentials.
- **Message format** (one line each, Slack mrkdwn):
  - On success (something committed): `:white_check_mark: daily-obsidian-vault-commit <YYYY-MM-DD> — committed <short SHA>, <N> files changed.`
  - On no-op (clean tree): `:information_source: daily-obsidian-vault-commit <YYYY-MM-DD> — nothing to commit.`
  - On failure: `:x: daily-obsidian-vault-commit <YYYY-MM-DD> — <step> failed (<short reason>). See routine output for details.`

Slack is best-effort — it is **not** part of the routine's success criteria. If the Slack call fails or the server is unauthenticated, log the failure inline in the routine's text output and continue. The routine output is the source of truth either way.

## Success criteria

The routine is considered successful only when **one** of the following holds:

1. Step 2 found a clean working tree → _No-op_ block printed.
2. Steps 3–5 completed: every change staged, a commit landed on `main` with a synthesized message, and the _Success_ block was printed. Step 6 may be empty or non-empty; either is fine.

Step 7's outcome (`updated` / `skipped` / `failed`) does **not** affect routine success — only Steps 1–5 do.

Any aborted step (1, 3, or 5) is a failure regardless of how far the routine got.

## Failure handling summary

| Step | Failure mode                           | Action                                                                                                                                                                            |
| ---- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Branch ≠ `main`                        | Stop. Do not auto-switch branches. Report actual branch in output.                                                                                                                |
| 2    | `git status` errors                    | Stop. Likely repo corruption — investigate manually before next run.                                                                                                              |
| 3    | `git add -A` errors                    | Stop. Could be a permission issue or a refused large file. Report the offending path.                                                                                             |
| 4    | Diff too large / synthesis fails       | Fall back to `Daily snapshot — N files changed`. Still commit. Not a failure.                                                                                                     |
| 5    | Pre-commit hook rejects the commit     | Stop. Do **not** retry with `--no-verify`. Leave changes staged. Report hook output verbatim.                                                                                     |
| 6    | Observation pass errors                | Log inline and proceed. Non-fatal.                                                                                                                                                |
| 7    | `graphify.sh update` fails / times out | Report `Graph: failed (<reason>)` in the Success block; include last ~10 stderr lines in Details. Routine still succeeds; `needs_update` flag persists so tomorrow's run retries. |
