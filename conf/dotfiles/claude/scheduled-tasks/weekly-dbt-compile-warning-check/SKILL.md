---
name: weekly-dbt-compile-warning-check
description: Compile Warnings — Weekly Zero-Warning Check
---

# Compile Warnings — Weekly Zero-Warning Check

**Trigger:** Every Monday 08:00 | **Tenant:** `t_logineko`

> All commands require `dangerouslyDisableSandbox: true` — git needs SSH, dbt needs GCP.

## Step 1 — Pull latest main

```bash
git checkout main
git pull --ff-only origin main
```

## Step 2 — Compile

```bash
cd tools
LOG="/tmp/weekly-compile-warnings.log"
uv run dbt_job.py t_logineko sandbox compile --no-partial-parse --show-all-deprecations > "$LOG" 2>&1
```

If `compile_rc != 0`: surface the tail of `$LOG` verbatim and post the failure verdict.

## Step 3 — Count warnings

dbt wraps the `[WARNING]` token in ANSI color codes (raw bytes look like `[<ESC>[33mWARNING<ESC>[0m]`), so the literal `[WARNING]` never appears in the raw log. **Strip ANSI BEFORE grepping** — otherwise the count is always 0 and the routine falsely reports SUCCESS.

```bash
CLEAN="/tmp/weekly-compile-warnings.clean.log"
perl -pe 's/\x1b\[[0-9;]*m//g' "$LOG" > "$CLEAN"
warn_count=$(grep -cE '\[WARNING\]' "$CLEAN")
grep -nE '\[WARNING\]' "$CLEAN"
```

- `warn_count == 0` → **SUCCESS**
- `warn_count > 0` → **FAILURE** — report count and list warnings grouped by kind (constraint / source-relationship / deprecation / other)

## Slack DM (best-effort, not success criteria)

Post a single-line verdict DM to the logged-in user. The user's Slack user_id is shown in the `slack_send_message` tool description — use it directly as `channel_id`.

- Success: `:white_check_mark: weekly-compile-warnings <YYYY-MM-DD> — compile clean, 0 warnings.`
- Failure (warnings): `:x: weekly-compile-warnings <YYYY-MM-DD> — <N> compile warning(s). See routine output for details.`
- Failure (compile error): `:x: weekly-compile-warnings <YYYY-MM-DD> — compile failed (exit <rc>). See routine output for details.`

If the Slack call fails, log the error inline — the routine output is the source of truth.