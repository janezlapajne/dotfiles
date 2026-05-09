---
name: weekly-working-hours
description: Working Hours Report — Weekly Build Check
---

# Routine: Working Hours Report — Weekly Build Check

## Metadata

| Field         | Value                                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------------------- |
| Trigger       | Every Tuesday at 08:00                                                                                |
| Purpose       | Verify that the `working_hours_report` models build successfully and the data passes error-detection. |
| Tenant        | `t_logineko`                                                                                          |
| Target models | `datamarts/tenants/t_logineko/models/working_hours_report`                                            |
| Branch        | `schedule-working-hours`                                                                              |
| dbt target    | `u_janezlapajne_schedule_working_hours`                                                               |
| Execution env | Local worktree of `farming-data-layer`, created with the `worktrunk` (`wt`) tool.                     |

## Workflow

The routine runs the steps below **in order**. A step must succeed before the next one starts. If any step fails, stop and follow the *On failure* guidance for that step.

### Step 1 — Sync `main`

Run from the main `farming-data-layer` checkout (not inside a worktree):

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
```

**Expected outcome:** Local `main` is fast-forwarded to `origin/main`.

### Step 2 — Create an isolated worktree

If a worktree for `schedule-working-hours` already exists from a prior run (clean or not), always remove it first to guarantee a deterministic, fresh starting state:

```bash
wt remove schedule-working-hours    # alias: wtr schedule-working-hours
```

Then set the dbt-target variable and create the worktree:

```bash
wt config state vars set dbt-target=u_janezlapajne_schedule_working_hours --branch=schedule-working-hours   # alias: wtv dbt-target=u_janezlapajne_schedule_working_hours --branch=schedule-working-hours
wt switch --create schedule-working-hours                                                                    # alias: wtc schedule-working-hours
```

- The first command sets the `dbt-target` variable for the new worktree environment.
- The second command creates the worktree on branch `schedule-working-hours`.

> **Note on shell aliases:** `wtv`, `wtc`, and `wtr` are zsh aliases (`wt config state vars set`, `wt switch --create`, `wt remove`). If aliases are unavailable in the running environment, use the long forms shown above.

**All remaining steps must be executed inside the newly created worktree.**

### Step 3 — Reset the BigQuery sandbox

The `justfile` lives in `tools/`, so run from there:

```bash
cd tools
just bq_reset_env --yolo
```

**Expected outcome:** Sandbox dataset is wiped and recloned, giving the build a clean starting state.

### Step 4 — Build the working hours reports

Run from the `tools/` directory of the worktree so `.env` / `.env.default` load correctly:

```bash
cd tools
uv run dbt_job.py t_logineko sandbox build \
  --select +working_hours_report__night_shift_working_hours_report \
           +working_hours_report__monthly_working_hours_report
```

**Expected outcome:** All selected models build successfully and all tests pass.

**On failure:** Investigate the failing model or test. Do **not** proceed to Step 5 until Step 4 is green.

### Step 5 — Run the custom error-detection check

Also run from the `tools/` directory of the worktree:

```bash
cd tools
uv run dbt_job.py t_logineko sandbox run \
  --select +working_hours_report__shift_schedule_working_hours_error_detection
```

This run materializes the error-detection view. **Important:** the wrapper exits `0` as long as the SQL compiles and the view is created — it does **not** count rows. After the run completes, query the resulting view and confirm it has zero rows:

```bash
bq query --use_legacy_sql=false --format=prettyjson --nouse_cache \
  'SELECT COUNT(*) AS row_count
   FROM `login-eko-data-layer-dev.dev__u_janezlapajne_schedule_working_hours__t_logineko__working_hours_report.shift_schedule_working_hours_error_detection`'
```

This model is a **custom test**: success means `row_count = 0`. Any non-zero count indicates erroneous data.

**Expected outcome:** The `dbt_job.py run` completes successfully **and** the row count is `0`.

**On failure:**
- If the `dbt_job.py run` errors → investigate the SQL / upstream model.
- If the row count is `> 0` → the data has an issue. Inspect the rows with:

  ```bash
  bq query --use_legacy_sql=false --format=prettyjson --nouse_cache \
    'SELECT * FROM `login-eko-data-layer-dev.dev__u_janezlapajne_schedule_working_hours__t_logineko__working_hours_report.shift_schedule_working_hours_error_detection`'
  ```

  Identify the affected `working_hours_report` records, include the offending rows and root-cause hypothesis in the routine output, and post the failure verdict per the *Slack notification* section below. Do not treat the routine as successful.

### Step 6 — Tear down the worktree

Run from outside the worktree, only after the routine has reported its result:

```bash
wtr schedule-working-hours
```

**Expected outcome:** Worktree is removed and the branch is cleaned up.

> **Note:** On failure in Steps 3–5, prefer **keeping** the worktree so the issue can be debugged. Only run `wtr` once the failure has been investigated or escalated.

## Slack notification (verdict only)

After the routine reaches a terminal state — success or failure — post one short Slack DM to the routine owner so they get a passive ping without opening the routine output. The owner reads the routine's text output for everything else (offending rows, queries, worktree path, etc.); Slack carries only the verdict.

- **Destination:** Direct message to the routine owner (self-DM in the authenticated workspace) — resolve identity from session context (e.g. the `# userEmail` block) rather than hard-coding it.
- **Channel:** Slack via the `plugin:slack:slack` MCP server.
- **Auth:** If the server reports as unauthenticated, call `mcp__plugin_slack_slack__authenticate` to start the OAuth flow, then `mcp__plugin_slack_slack__complete_authentication` with the callback URL. Subsequent runs reuse the stored credentials.
- **Message format** (one line each, Slack mrkdwn):
  - On success: `:white_check_mark: weekly-working-hours <YYYY-MM-DD> — build green, error-detection 0 rows.`
  - On failure: `:x: weekly-working-hours <YYYY-MM-DD> — <step> failed (<short reason, e.g. "error-detection returned N rows" or "Step 4 build failed">). See routine output for details.`

Slack is best-effort — it is **not** part of the routine's success criteria. If the Slack call fails or the server is unauthenticated, log the failure inline in the routine's text output and continue. The routine output is the source of truth either way.

## Success criteria

The routine is considered successful only when **all** of the following hold:

1. Step 4 (`build`) finishes with no errors and no failed tests.
2. Step 5 (error-detection model) returns zero rows.
3. Step 6 (worktree cleanup) completes — or is intentionally skipped due to a failure that requires debugging.

## Failure handling summary

| Step | Failure mode                        | Action                                                               |
| ---- | ----------------------------------- | -------------------------------------------------------------------- |
| 1    | `git pull` not fast-forward         | Reconcile `main` manually; do not force.                             |
| 2    | `wtc` fails (worktree already exists) | Always remove the prior worktree with `wtr schedule-working-hours`, then retry the create commands. |
| 3    | `just bq_reset_env` fails           | Check BigQuery auth/quotas; retry.                                   |
| 4    | Build or test failure               | Stop. Investigate the failing model. Do not advance.                 |
| 5    | Errors out                          | Treat as a build failure (investigate SQL / upstream).               |
| 5    | Row count > 0                       | Data quality issue. Inspect rows, identify root cause, include details in the routine output, and post the failure verdict per *Slack notification*. |
| 6    | `wtr` fails                         | Remove the worktree manually if needed.                              |