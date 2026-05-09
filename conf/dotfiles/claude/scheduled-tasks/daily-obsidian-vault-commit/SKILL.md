---
name: daily-obsidian-vault-commit
description: Obsidian Vault — Daily Commit
---

# Routine: Obsidian Vault — Daily Commit

## Metadata

| Field         | Value                                                                                         |
| ------------- | --------------------------------------------------------------------------------------------- |
| Trigger       | Daily                                                                                         |
| Purpose       | Snapshot all changes in the Obsidian vault to git on `main` with an agent-readable message.   |
| Vault         | `~/mydrive/brain/Notes`                                                                       |
| Branch        | `main` (commit only — repository has no remote, nothing is pushed).                           |
| Execution env | Local checkout of the vault. No worktree, no extra tooling.                                   |

## Workflow

The routine runs the steps below **in order**. A step must succeed before the next one starts. If any step aborts, follow the *Failure handling summary* and post the failure verdict per *Slack notification*.

All steps run from the vault root: `cd ~/mydrive/brain/Notes`.

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

If the output is empty, print the *No-op* block from *Routine output contract* and exit success. Skip the remaining steps.

Otherwise continue to Step 3.

### Step 3 — Stage everything

```bash
git add -A
```

Existing `.gitignore` is the only exclusion mechanism. Do **not** filter files manually here — anything the user wanted excluded should already be in `.gitignore`. Suspect entries are surfaced in Step 6, not silently dropped.

### Step 4 — Synthesize the commit message

Read the staged diff (`git diff --cached`) and write the message. Format is intentionally plain — `git log` plus `git log --name-status` is the parsing surface, so the message body is reserved for things git cannot synthesize on its own.

If the diff is very large (>~2000 lines), truncate before reading — a runaway diff must not blow the context window. In that case use the fallback subject below.

**Subject (required, 50–72 chars):**
- Natural-language summary in **content** terms — name the topics, ideas, sections, or templates that changed.
- Specifics over generics: `Expand systematic-debugging chapter and add weekly-review template` beats `Update notes`.
- **No** Conventional Commits prefix (`notes:`, `chore:`, etc.) — every commit would have the same prefix, so it adds no signal.
- **No** date, file count, or `Daily snapshot`-style phrasing — the date is already on the commit, the file list is in `git log --name-status`.

**Body (optional, 1–3 sentences):**
- Add only when the diff covers multiple unrelated themes that don't fit in the subject.
- Describe the themes in prose. Do **not** list files.

Examples:

```
Capture daily-commit skill design and expand systematic-debugging chapter
```

```
Reorganize project-management notes; add weekly-review template

Split the Areas/Projects PARA folder by lifecycle stage. New template under
Templates/weekly-review.md collects the prompts I've been using ad-hoc.
```

**Fallback (if synthesis fails or the diff was truncated):** use a generic subject of the form `Daily snapshot — N files changed` (where N is from `git diff --stat HEAD`). Still proceed to Step 5; do not abort.

### Step 5 — Commit

Pass the message via heredoc to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
<subject>

<optional body>
EOF
)"
```

**Do not** pass `--no-verify`. **Do not** amend a prior commit. **Do not** retry with skip-hook flags if a hook fails.

**On failure (hook rejected the commit, working tree changed mid-run, etc.):** Stop. Leave the changes staged on disk. Report the failing hook (or other reason) and its output verbatim in the routine output. Post the failure verdict per *Slack notification*.

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

## Routine output contract

The routine prints exactly one terminal block at the end. Stable headings make the output easy to skim and trivial to parse.

**Success (something committed):**

```
:white_check_mark: daily-obsidian-vault-commit <YYYY-MM-DD>
Commit: <short SHA> — <subject>
Files: <added>+ <modified>~ <deleted>-
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

## Slack notification (failure only)

Post a Slack DM **only** when the routine fails. Successes and no-op runs are silent — daily green pings are noise.

- **Destination:** Self-DM to the routine owner — resolve identity from session context (e.g. the `# userEmail` block) rather than hard-coding it.
- **Channel:** Slack via the `plugin:slack:slack` MCP server.
- **Auth:** If the server reports as unauthenticated, call `mcp__plugin_slack_slack__authenticate` to start the OAuth flow, then `mcp__plugin_slack_slack__complete_authentication` with the callback URL. Subsequent runs reuse the stored credentials.
- **Message format** (one line, Slack mrkdwn):

  ```
  :x: daily-obsidian-vault-commit <YYYY-MM-DD> — <step> failed (<short reason>). See routine output for details.
  ```

Slack is best-effort — it is **not** part of the routine's success criteria. If the Slack call fails or the server is unauthenticated, log the failure inline in the routine's text output and continue. The routine output is the source of truth either way.

## Success criteria

The routine is considered successful only when **one** of the following holds:

1. Step 2 found a clean working tree → *No-op* block printed.
2. Steps 3–5 completed: every change staged, a commit landed on `main` with a synthesized message, and the *Success* block was printed. Step 6 may be empty or non-empty; either is fine.

Any aborted step (1, 3, or 5) is a failure regardless of how far the routine got.

## Failure handling summary

| Step | Failure mode                                | Action                                                                                       |
| ---- | ------------------------------------------- | -------------------------------------------------------------------------------------------- |
| 1    | Branch ≠ `main`                             | Stop. Do not auto-switch branches. Report actual branch in output.                           |
| 2    | `git status` errors                         | Stop. Likely repo corruption — investigate manually before next run.                         |
| 3    | `git add -A` errors                         | Stop. Could be a permission issue or a refused large file. Report the offending path.        |
| 4    | Diff too large / synthesis fails            | Fall back to `Daily snapshot — N files changed`. Still commit. Not a failure.                |
| 5    | Pre-commit hook rejects the commit          | Stop. Do **not** retry with `--no-verify`. Leave changes staged. Report hook output verbatim.|
| 6    | Observation pass errors                     | Log inline and proceed. Non-fatal.                                                           |
