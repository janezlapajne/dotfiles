---
name: fdl-worktree-create
description: Set up an isolated farming-data-layer worktree (per-branch dbt-target). Use whenever starting any new change, fix, feature, or investigation in the farming-data-layer repo — typically after the user pastes a GitLab issue or MR URL, asks to "investigate", "look into", "fix", or "create a worktree". Refuses to run inside an existing worktree. Creates an MR linked to the issue only when one does not already exist (or the existing one has commits); never creates a new issue.
allowed-tools: Bash(wt:*), Bash(wts:*), Bash(wtc:*), Bash(wtv:*), Bash(git fetch:*), Bash(git checkout:*), Bash(git pull:*), Bash(git rev-parse:*), Bash(git rev-list:*), Bash(glab mr view:*), Bash(glab mr list:*), Bash(glab mr create:*), Bash(glab issue view:*), Bash(jq:*), Read
---

# fdl-worktree-create

## Overview

Set up an isolated git worktree for new work in the farming-data-layer project (changes, fixes, features, investigations). Every task gets its own worktree and its own `dbt-target` state var so parallel dev work cannot collide in BigQuery.

**This skill is orchestration only.** It refuses to run inside an existing worktree, optionally creates a Draft MR against an existing GitLab issue (it never creates a new issue), then uses `wt` (worktrunk) to create and enter the worktree. All follow-up work runs inside the new worktree, not the main checkout.

## When to Use

- User pastes a GitLab issue URL (e.g. `https://gitlab.com/.../-/issues/898`).
- User pastes a GitLab MR URL (e.g. `https://gitlab.com/.../-/merge_requests/671`).
- User asks to "investigate" something, "look into" a problem, "fix" something, or "create a worktree".
- Any time non-trivial work is about to start and you are currently in the main checkout.

## When NOT to Use

- You are already inside a worktree — the skill will refuse anyway, but don't trigger it.
- The user is asking a read-only question (just looking up data, reading a file).
- A worktree for the same MR/branch already exists and you can be sure of it — just `wts mr:<NUM>` or `wt switch <branch>` directly.

## Workflow

The steps run **in order**. A step must succeed before the next starts. On failure, stop and report which step failed — do not silently recover.

### Step 0 — Refuse if already inside a worktree

```bash
wt list --format=json | jq -r '.[] | select(.is_current and (.is_main | not)) | .path'
```

If the command prints any path, you are inside a non-main worktree. Stop immediately and tell the user:

> You are currently inside a worktree (`<path>`). This skill must be run from the main checkout at `~/programs/login/farming-data-layer`. Switch back first (e.g. `wt switch main` or `cd ~/programs/login/farming-data-layer`) and re-run.

Do not proceed.

If the command prints nothing, you are at the main checkout — continue.

### Step 1 — Classify the input

Detect which of three modes applies from the user's most recent message:

1. **MR URL provided** — the URL contains `/-/merge_requests/<NUM>`. Extract `MR_NUM`. Fetch the MR:

   ```bash
   glab mr view <MR_NUM> --output=json
   ```

   Read `source_branch`, `state`, and the linked issue reference from the description (`Closes #<ISSUE_NUM>` if present). Go to **Step 1b**.

2. **Issue URL provided** — the URL contains `/-/issues/<NUM>`. Extract `ISSUE_NUM`. Look for an open MR already linked to this issue and assigned to the current user:

   ```bash
   glab mr list --state=opened --assignee=@me --search="Closes #<ISSUE_NUM>" --output=json
   ```

   If that returns nothing, fall back to:

   ```bash
   glab issue view <ISSUE_NUM> --output=json | jq '.related_merge_requests // .merge_requests // []'
   ```

   - **Existing open MR found** → set `MR_NUM` + `source_branch` from it, go to **Step 1b**.
   - **No MR exists** → go to **Step 1c**.

3. **Nothing provided** — neither URL is in the message. Local-only mode. **Always infer** a short topic name from conversation context (the user's most recent message, recent file activity, the issue title if one was discussed earlier). Never ask. Go to **Step 2**.

### Step 1b — Decide whether to reuse an existing MR

Check whether the MR's branch already has commits beyond `origin/main`:

```bash
git fetch origin
COUNT=$(git rev-list --count origin/main..origin/<source_branch> 2>/dev/null || echo 0)
```

- **`COUNT == 0`** (branch is empty) → reuse the MR. Set `BRANCH_NAME = <source_branch>` and `MR_REUSED=true`. Go to **Step 2**.
- **`COUNT > 0`** (branch already has commits) → do **not** reuse. Print:

  > Existing MR !<MR_NUM> has <COUNT> commits — creating a new MR instead.

  Then:
  - If the original input was an **issue URL** (or the existing MR's description has `Closes #<ISSUE_NUM>`) → go to **Step 1c** with that `ISSUE_NUM`.
  - If the original input was an **MR URL with no linked issue** → fall through to local-only mode (Step 2), no remote MR.

### Step 1c — Create a fresh Draft MR linked to the existing issue

Runs only when there is a known `ISSUE_NUM` and no usable MR. Never creates a new issue.

1. Fetch the issue title for the MR title:
   ```bash
   glab issue view <ISSUE_NUM> --output=json | jq -r '.title'
   ```
2. Pick `DECIDE` from the issue title — short snake_case, ≤ 20 chars, no leading digits. Examples: `schema_error`, `pumpa_split`, `rpt_cleanup`.
3. Set `BRANCH_NAME = <ISSUE_NUM>-<DECIDE>` (project convention seen in commits like `888-separate-15-minute-pipeline-for-sm-pumpa-dashboards`).
4. Create the branch server-side and a Draft MR assigned to the current user:
   ```bash
   glab mr create \
     --repo "login5/login-eko/reports/farming-data-layer" \
     --title 'Resolve "<issue title>"' \
     --description "Closes #<ISSUE_NUM>" \
     --source-branch "<BRANCH_NAME>" \
     --target-branch main \
     --assignee "@me" \
     --draft \
     --create-source-branch \
     --remove-source-branch \
     --yes \
     --no-editor
   ```
   Flag rationale:
   - `--repo` — explicit project path; avoids relying on the cwd's git remote.
   - `--remove-source-branch` — branch auto-deletes when the MR merges (hygiene).
   - `--no-editor` — never opens `$EDITOR`; required for non-interactive use.
   - `--yes` — skip confirmation prompts.
   - `--draft` — owns the draft status; it prepends the `Draft:` title prefix itself. **Do not** also put `Draft:` in `--title`, or GitLab renders `Draft: Draft: …` (the second is literal text). The `--title` value must be the bare title.
5. Capture the new `MR_NUM` from the URL printed on stdout. Set `MR_REUSED=false`.

### Step 2 — Resolve `DECIDE`, `TARGET_VAR`, `BRANCH_NAME`

If not already set by Step 1b/1c:

- **`DECIDE`** — snake_case, ≤ 20 chars, no leading digits. Inferred from issue title, MR title, or conversation context. Examples: `schema_error`, `pumpa_split`, `rpt_cleanup`, `dim_fact_rpt`.
- **`TARGET_VAR = u_janezlapajne_<DECIDE>`** — used as the dbt target. Per-worktree, so different worktrees never write to the same dev warehouse target.
- **`BRANCH_NAME`** —
  - MR/issue mode with reused MR → `<source_branch>` (verbatim).
  - Fresh MR from Step 1c → `<ISSUE_NUM>-<DECIDE>`.
  - Local-only mode → `<DECIDE>`.

### Step 3 — Sync `main` from the main checkout

```bash
cd ~/programs/login/farming-data-layer
git fetch origin
git checkout main
git pull --ff-only origin main
```

**Expected:** local `main` fast-forwards to `origin/main`.

**On failure:** report which command failed (especially if the fast-forward is refused — that means local `main` has diverged and needs manual cleanup). Stop. Do not attempt to recover, rebase, or reset.

### Step 4 — Set the per-branch `dbt-target` state var

This must run **before** the worktree is created so the `[post-start]` hook in `~/.config/worktrunk/config.toml` sees it.

```bash
wt config state vars set dbt-target=<TARGET_VAR> --branch=<BRANCH_NAME>
```

### Step 5 — Create or enter the worktree

Use the matching form for the resolved mode:

- **MR-linked, branch exists remotely** (reused MR, or fresh MR from Step 1c — the branch was created server-side):

  ```bash
  wts mr:<MR_NUM>
  ```

  The `wts mr:<NUM>` shim resolves the MR's source branch and switches into its worktree (creating it if missing).

- **Local-only mode, brand-new branch**:

  ```bash
  wt switch --create <BRANCH_NAME>
  ```

- **Branch already exists locally but no MR shortcut applies**:
  ```bash
  wt switch <BRANCH_NAME>
  ```

`wt` handles the directory change and runs the project's `[post-start]` hook automatically.

### Step 6 — Report and hand off

Print a concise summary the user can verify at a glance:

```
Worktree:    <path printed by wt>
Branch:      <BRANCH_NAME>
dbt-target:  <TARGET_VAR>
MR:          !<MR_NUM>  <url>     (or "local-only — no MR")
```

Then say explicitly:

> All remaining work for this task runs inside the new worktree.

Stop. Do not start the actual work — that is the next user turn's job.

## Important Rules

- **Never** create a new GitLab issue from this skill. Only MRs.
- **Never** run any `git` write operation other than `git fetch`, `git checkout main`, `git pull --ff-only origin main` (Step 3) and the implicit branch creation done by `glab mr create --create-source-branch` (Step 1c). All branch and worktree manipulation goes through `wt` and `glab`.
- **Never** call the `glab-create-ticket` skill from here — it creates an issue + MR pair, which is the wrong shape. Use `glab mr create` directly.
- **Never** edit project files, run dbt, or do any of the actual task work in this skill. This skill stops once the worktree is ready.
- If Step 0 detects you are inside a worktree, the skill ends there — no fallback, no auto-switch back to main.

## Common Mistakes

- **Setting `dbt-target` after `wt switch`** — too late; the `[post-start]` hook already ran without the var. Always do Step 4 before Step 5.
- **Reusing an MR that already has commits** — those commits become entangled with new work. Always check Step 1b before reusing.
- **Using `wt switch --create` for an MR branch that already exists server-side** — will fail or create a divergent local branch. Use `wts mr:<NUM>` for MR-linked branches.
- **Forgetting `--ff-only` on `git pull`** — if local `main` has diverged, a default `git pull` may merge or rebase silently. The skill must abort instead.
- **Picking a `DECIDE` longer than 20 chars or with leading digits** — breaks the `u_janezlapajne_<DECIDE>` target convention.
