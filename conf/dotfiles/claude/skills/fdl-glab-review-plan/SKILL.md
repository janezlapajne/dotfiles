---
name: fdl-glab-review-plan
description: Use when the user provides a GitLab merge request URL and wants an ordered, executable implementation plan derived from the open (non-resolved) reviewer discussions on that MR. The plan includes implement + validate + post-resolution steps per task, then one final cleanup task that deletes the user's original pre-plan notes, so the next turn can close each thread end-to-end. Triggered manually only.
disable-model-invocation: true
allowed-tools: Bash(glab:*), mcp__gitlab__whoami, mcp__gitlab__get_merge_request, mcp__gitlab__mr_discussions, mcp__gitlab__get_merge_request_file_diff, Read, AskUserQuestion
---

# fdl-glab-review-plan

## Overview

Turns reviewer feedback on an open GitLab MR into an ordered task list **the next-turn executor** can run. This skill is **read-only**: it inspects the MR, groups discussions, and emits a plan to chat. It never edits files and never writes to GitLab.

The "next-turn executor" is whatever runs the plan in a *following* turn — by default, plain Claude reading this plan back from context (no separate skill is required). This skill only prints the plan; it never performs the Implement / Validate / Post / Cleanup steps itself.

Reviewer discussions that the user (`@<plan_user>`) has annotated in-thread with a leading number (e.g. `1`, `2.`, `(3)`) get grouped into one atomic task per number. Threads where the user gave a non-numbered reply — or no reply at all — become independent items at the end of the plan.

Each emitted task is self-contained and includes three steps in fixed order:

1. **Implement** — the concrete code change the executor should make.
2. **Validate (gate)** — explicit pass/fail checks confirming the change actually addresses every reviewer ask grouped into this task. If validation fails on a thread, the executor must **skip Step 3 for that thread** and report the gap to the user instead of posting a misleading resolution.
3. **Post resolution** — a single reply added under each reviewer comment that passed Step 2, with the canonical `Resolved in <sha>: …` body.

After every task's Step 3 has run, the plan ends with one **Final cleanup** task that deletes the user's *original* pre-plan notes (everything `@<plan_user>` wrote before the plan was emitted) while preserving the fresh resolution replies. Cleanup runs last, once, across every thread — not per task. Its full rules live in the [Final cleanup](#final-cleanup--delete-your-original-pre-plan-notes-run-last-once) section.

The plan is the contract between this skill and the executor. Everything needed to close the task must be on the page; nothing implicit.

## When to use

- User pastes a GitLab MR URL and asks for "the plan to address reviews", "review tasks", "let's start fixing comments", or similar.
- MR is in `opened` state and has non-resolved discussions.
- The intent is to *prepare* the work, not execute it. Execution happens in a following turn against the printed plan, run by a separate skill.

## When NOT to use

- MR is merged, closed, or has no open discussions → return a single-line summary instead.
- User wants to actually edit files now — let the next-turn executor do that against the plan this skill emits. This skill never touches the repo.
- User wants this skill to delete notes / post replies on GitLab — it won't. The plan describes those steps; the executor performs them.

## Inputs

Required: GitLab MR URL.

If missing, ask **once** via `AskUserQuestion` with header `MR URL`, then stop if still missing. Accept both:
- `https://gitlab.com/<group>/<subgroup>/<project>/-/merge_requests/<iid>`
- Self-hosted equivalents on a different host.

Parse into `{host, project_path, mr_iid}`. URL-encode `project_path` when calling APIs.

## Determine the planning user (the assignee)

The **planning user** (`@<plan_user>`) is the person whose in-thread notes drive task grouping and whose pre-plan notes Final cleanup deletes. Their comments are read **directly as instructions to the executor**, so resolving the wrong user silently corrupts the whole plan — get this right before anything else. Do **not** hardcode a username; resolve it from the MR each run.

Resolve `<plan_user>` from the MR's `assignees`, in this order (first match wins):

1. **Exactly one assignee** → use that assignee's `username`. No confirmation needed.
2. **Two or more assignees** → ambiguous. Ask the user **once** via `AskUserQuestion` (header `Assignee`) to pick whose comments should be read as the plan instructions; offer each assignee `username` as an option. If the authenticated account (`mcp__gitlab__whoami`, or `GITLAB_HOST=<host> glab api user`) is among the assignees, list it first and mark it `(Recommended)` — it is most likely the one running the plan. Use the chosen `username` as `<plan_user>`.
3. **No assignee on the MR** → fall back to the authenticated account running this skill (`mcp__gitlab__whoami`, or `GITLAB_HOST=<host> glab api user`). Use its `username` as `<plan_user>`.
4. **Step 3 fallback also fails** (no assignee AND whoami unavailable) → ask **once** via `AskUserQuestion` (header `Assignee`) for the GitLab username whose notes drive the plan; stop if still unknown.

Use the GitLab `username` field exactly as the API returns it (e.g. `jane.doe`) — note it may differ from the git **commit author** name (e.g. `janedoe`); always match on the GitLab username, never the commit author. Every "did the planning user reply?" check in the phases below compares discussion note `author.username == "<plan_user>"`. Throughout this document `@<plan_user>` is a placeholder for the resolved username — substitute the real value when emitting the plan.

## Tool selection — probe at runtime

Prefer the `glab` CLI when it is installed **and** authenticated; otherwise fall back to the GitLab MCP tools. Probe in this order:

```bash
if command -v glab >/dev/null 2>&1 && glab auth status >/dev/null 2>&1; then
    TOOL=glab
else
    TOOL=mcp
fi
```

If `glab` is installed but `glab auth status` fails (e.g. an OAuth/TLS hiccup on this host), fall back to MCP — do not abort.

**Host:** the `<host>` parsed from the URL must reach every `glab` call, or self-hosted MRs hit the wrong server. Pass `-R <host>/<project_path>` to the `mr` subcommands, and prefix `glab api` calls with `GITLAB_HOST=<host>`. For gitlab.com the host prefix is harmless, so always include it rather than branching.

| Operation | `glab` | MCP fallback |
|---|---|---|
| MR metadata | `glab mr view <iid> -R <host>/<project_path> --output json` | `mcp__gitlab__get_merge_request` |
| Discussions | `GITLAB_HOST=<host> glab api projects/<encoded>/merge_requests/<iid>/discussions --paginate` | `mcp__gitlab__mr_discussions` |
| File diff (optional context) | `glab mr diff <iid> -R <host>/<project_path>` | `mcp__gitlab__get_merge_request_file_diff` |

## Workflow

### Phase 1 — Validate

1. Parse the URL. If unparseable, ask once and stop on failure.
2. Probe tool selection (above).
3. Fetch MR metadata (must include `assignees`). If `state != "opened"`, print one line (`MR !<iid> is <state> — nothing to plan.`) and stop.
4. Resolve `<plan_user>` from the MR's assignees per [Determine the planning user](#determine-the-planning-user-the-assignee). If resolution can't settle on a username (ambiguous fallback unanswered), stop.

### Phase 2 — Fetch discussions

Pull every discussion on the MR (paginate). Keep only those where:
- The first note has `resolvable: true` AND `resolved: false`.
- The first note has `system: false` (skip "added 3 commits", "marked as draft", etc).

If zero discussions remain, print `No open discussions on MR !<iid>.` and stop.

Discussions that are already `resolved == true` are excluded here and are **out of scope for the entire run**: they never enter a task, never appear in the plan, and their notes are **never deleted or modified** by Final cleanup. Resolved threads — and every `@<plan_user>` comment inside them — are preserved as-is.

### Phase 3 — Parse each open discussion

For each surviving discussion, extract from the **first note**:
- `reviewer = author.username`
- `body` (reviewer's comment text)
- File and line from `position`:
  - Prefer `new_path` + `new_line`.
  - Fall back to `old_path` + `old_line` for deletion comments.
  - If `position` is `null`, this is a general MR thread — record `file = "(general thread)"`, no line.
- `head_sha = position.head_sha` (or MR head SHA for general threads)
- Permalink: `<mr_web_url>#note_<first_note_id>`

Then walk the remaining notes in the discussion. For every note where `author.username == "<plan_user>"`, record `note_id`, `created_at`, and `body`, then:
- Strip leading whitespace.
- **Group number** — match the first integer token using this regex (apply in order, first match wins):
  - `^#?\(?(\d+)\)?\s*[.)\-:]?\s*` — captures `1`, `1.`, `1)`, `(1)`, `#1`, `1 -`, `1:`
  - If a note's entire body is just a bare integer (after trim), that integer is the group.
  - No match → this note carries no group number (but it is still one of the user's pre-plan notes — see Phase 5 cleanup collection).
- **Direction text** — note body with the group-number prefix stripped. Direction is **empty** if any of these hold: the whole reply was a digit; **or** the body matches one of this skill's own canonical output shapes (`Resolved in <sha>: …` or `Out of scope: …`). The canonical-shape case is a stale resolution note left in the thread by a prior run — it is *not* an instruction to the executor, so it must never become direction text. (It is still collected as a baseline reference for Final cleanup — see Phase 5.)

If multiple user notes exist in the same thread:
- Group number: use the **latest** numbered note. If none of them are numbered, the thread is ungrouped.
- Direction text: concatenate all non-empty direction snippets (numbered and un-numbered) in chronological order, separated by `; ` — so an un-numbered follow-up like `also handle nulls` is preserved as direction, not dropped. Snippets emptied by the canonical-shape rule above contribute nothing.

### Phase 4 — Group into tasks

- Threads sharing a group number → one **Task N**.
- Threads without a group number (no reply, or unnumbered replies) → individual items under **Ungrouped**, sorted by `(file, line)` for stable ordering.
- **Task-level "Your direction"** (for a task spanning multiple threads) — concatenate the per-thread direction texts of every thread in the group, in thread order (sorted by `(file, line)`), separated by `; `, dropping empties. If every thread's direction is empty, the task has no direction and Step 1 derives the work from the reviewer asks instead.

### Phase 5 — Emit the plan

Print to chat using the template below. No file write.

Record two cutoff anchors and print both in the header:

- **`plan_emit_time`** — an ISO-8601 UTC timestamp. This is the cutoff for *notes*: it separates the user's *original* notes (`created_at <= plan_emit_time` → deleted in Final cleanup) from the *resolution replies* the executor posts during the run (`created_at > plan_emit_time` → kept). Notes carry a `created_at`, so a timestamp is the right key here.
- **`base_sha`** — the current head SHA of `<source_branch>` at plan-emit (the MR head SHA you already fetched). This is the cutoff for *commits*, used by the Step 2 gate. Do **not** reuse `plan_emit_time` for the commit check: `git log --since` keys off commit dates, which are timezone-sensitive, clock-skewed against the planning host, and rewritable. `git log <base_sha>..<source_branch>` is exact.

For every covered thread, collect **all** `@<plan_user>` notes whose `created_at <= plan_emit_time` — both numbering markers and any un-numbered instruction notes the user added for the executor. For each such note, record three things as a **baseline reference**: its `note_id`, its permalink (`<mr_web_url>#note_<note_id>`), and its **verbatim body**. These baseline references are printed per thread in the plan (they are both the record of what drove each task and the delete-list for the single Final cleanup task). Capturing the body verbatim matters: Final cleanup deletes these notes, so the plan is the only surviving record of the comments the tasks were generated from.

## Output template

Each task block contains three numbered steps in fixed order. The executor MUST run them in that order: Implement → Validate → Post resolution. Step 2 is the gate — when validation fails for a thread, Step 3 MUST be skipped for that thread and the failure surfaced to the user. After every task's Step 3 has run, the executor runs the single **Final cleanup** task once, across all threads.

```markdown
# Review adaptation plan — MR !<iid>: <title>

Source: `<source_branch>` → `<target_branch>` (head `<short_sha>`)
Project: `<project_path>`  •  MR IID: `<iid>`
Open discussions: <N>  •  Grouped tasks: <M>  •  Ungrouped: <K>
Plan emitted at: `<plan_emit_time>` (ISO-8601 UTC — cutoff for Final cleanup: only `@<plan_user>` notes created at or before this instant are deleted; resolution replies posted after it are kept)
Commit baseline: `<base_sha>` (head of `<source_branch>` at plan-emit — Step 2 checks `git log <base_sha>..<source_branch>` for new work)

## Task <number> — <short summary derived from your direction>

**Your direction:** <concatenated direction text — verbatim, no rewording>

**Covers <n> reviewer thread(s):**
- @<reviewer> on `<file>`:<line> — "<first ~120 chars of reviewer body>…"
  Discussion ID: `<discussion_id>`  •  First note ID: `<note_id>`  •  Permalink: <permalink>
  Reviewer asks (atomic): <bullet list — one bullet per distinct ask in the reviewer's body; this is the validation checklist for step 2>
  Your baseline notes (drove this task; deleted in Final cleanup — recorded here verbatim so the record survives deletion):
    - note `<note_id_a>` (`created_at <= plan_emit_time`) — <permalink_a> — "<verbatim body, e.g. `1`>"
    - note `<note_id_b>` (`created_at <= plan_emit_time`) — <permalink_b> — "<verbatim body, e.g. `also handle nulls`>"
- @<reviewer2> on `<file2>`:<line2> — "<…>"
  Discussion ID: `<discussion_id_2>`  •  First note ID: `<note_id_2>`  •  Permalink: <permalink_2>
  Reviewer asks (atomic): <…>
  Your baseline notes (drove this task; deleted in Final cleanup — recorded verbatim):
    - note `<…>` (`created_at <= plan_emit_time`) — <permalink> — "<verbatim body>"

### Step 1 — Implement

<one or more concrete code-change actions derived from your direction; if direction is empty, derive from the reviewer's ask. Reference file:line and what the new code should look like at a sketch level.>

Commit message suggestion: `<short imperative line, e.g. "models: split STRUCT properties onto one per line">`

### Step 2 — Validate (gate before any posting)

For every discussion in this task, confirm each line below evaluates true. **If any check fails, do NOT proceed to Step 3 for that thread — skip the post and report the gap to the user instead.**

- [ ] Source branch has at least one new commit since the plan was emitted (`git log <base_sha>..<source_branch>` is non-empty), **or** the task's direction is explicitly "out of scope".
- [ ] Each `file:line` referenced by the covered discussions is touched by the new commit(s), **or** the reviewer's ask was file-level / structural and the file is still touched.
- [ ] Each bullet under "Reviewer asks (atomic)" above is semantically satisfied by the diff — verified item by item, not in aggregate. (E.g. reviewer asked "rename X and add a comment" → both the rename and the comment must be present.)
- [ ] For threads where the reviewer has now marked `resolved=true` (someone else closed it while the task ran), mark the thread as "skip Step 3" and continue — not a failure, but no resolution post should be made.

Validation is per-thread, not per-task: if a task spans three threads and two pass while one fails, post resolutions on the two and report the gap on the third.

**If a thread fails validation**, emit a clearly-labelled block to chat (do not proceed to Step 3 for that thread):

```
⚠ Task <N> — validation failed on discussion <permalink>
- Reviewer ask not covered: <which bullet from the atomic list>
- What was checked: <commits inspected, files diffed>
- Why it didn't match: <one-sentence explanation>
- Action: re-implement or re-run after the missing change ships. Resolution NOT posted.
```

The user must see every unresolved item — do not silently swallow. A thread that fails here is also **excluded from Final cleanup** — leave the user's original notes in place so the rerun still has the context.

### Step 3 — Post resolution reply (only for threads that passed Step 2)

For each thread that passed Step 2 and is not already `resolved=true`, post exactly one fresh reply, threaded under the reviewer's first note. Canonical body:

```
Resolved in <short_sha>: <one sentence on what changed and why it satisfies the reviewer's ask>. <optional: verification done — tests, manual run>.
```

- `<short_sha>` is the 7-char prefix of the implementing commit on `<source_branch>`. Multiple commits → comma-separate.
- "Won't do" outcomes use: `Out of scope: <reason captured in your direction>.` (no SHA).
- Never `@`-mention the reviewer; the reply already threads under their note.
- Post the fresh reply even if a stale identical-bodied `@<plan_user>` note from a prior run still sits in the thread — that stale duplicate is a pre-plan note and gets removed in Final cleanup. Do **not** skip the post to avoid a duplicate; the cleanup, not the post step, resolves duplicates.

After all Step 3 posts for the task succeed, emit a one-line per-task close summary to chat:
`Task <N> resolved — <X> discussion(s) replied, <S> skipped (see ⚠ blocks above). Original notes will be removed in Final cleanup.`

If any thread reached the close summary with a non-zero `<S>`, the task is **partially closed**, not closed. The user has the ⚠ blocks; they decide whether to re-run.

---

## Ungrouped — independent items

### U1 — @<reviewer> on `<file>`:<line>
Reviewer: "<short quote>"
Your reply: <verbatim, or "(no reply)">
Discussion ID: `<discussion_id>`  •  Permalink: <permalink>
Your baseline notes (deleted in Final cleanup — recorded verbatim): `<note_id>` — <permalink> — "<verbatim body>" (or "(none)")

Reviewer asks (atomic): <bullet list>

**Step 1 — Implement:** <…>
**Step 2 — Validate (gate):** <same checklist as Task block, scoped to this single thread; on failure emit ⚠ block, skip Step 3, and exclude this thread from Final cleanup>
**Step 3 — Post resolution:** <canonical body sketch — only if Step 2 passed>

---

## Final cleanup — delete your original pre-plan notes (run last, once)

Run this **after every task's Step 3 has completed**, once, across all threads. It removes only the notes you wrote *before* this plan existed; it must leave the resolution replies just posted untouched.

For each thread that **passed Step 2** (skip threads still in a ⚠ failed state — keep their original notes for the rerun):

- Delete every `@<plan_user>` note listed under "Your baseline notes" for that thread. These are exactly the notes with `created_at <= <plan_emit_time>`: numbering markers (`1`, `2 use CTE`), any un-numbered instructions you added for the executor, and stale duplicate resolution notes from prior runs. Their verbatim bodies are already recorded in the plan above, so deleting them loses nothing.
- **Never** delete a note with `created_at > <plan_emit_time>` — that is a resolution reply this run posted in Step 3. Keep it.
- **Never** touch a thread that was already `resolved == true` (those are excluded from the plan entirely — see Phase 2). Comments under resolved threads are preserved, full stop.
- **Never** delete the reviewer's first note, or any note authored by anyone other than `<plan_user>`.
- **Guard — classify each pre-plan note by *exclusion*, not by judgment.** Apply these three tests in order; the first match decides:
  1. Body matches the **group-number marker** regex (`1`, `2 use CTE`, `(3)`, …) → **delete** (it's an executor instruction).
  2. Body matches this skill's **canonical output shape** — `Resolved in <sha>: …` or `Out of scope: …` → **delete** (it's a stale prior-run resolution; Step 3 re-posts a fresh equivalent). This is why it is *not* treated as a substantive reply.
  3. Matches neither → **hold for review**: it is a free-form note that may be a real answer to the reviewer (e.g. `agree, will rename`). Do **not** blind-delete; list it back to the user and ask first.
  This exclusion order resolves the apparent conflict with "delete stale duplicates": a `Resolved in <sha>:` note is caught by test 2 (delete), never falling through to test 3 (hold).
- A 404 on delete = already gone; keep going. A 403 = stop for that thread and surface to the user.

Emit a final summary line:
`Final cleanup — <I> original note(s) deleted across <T> thread(s), <D> stale duplicate(s) removed, <P> resolution reply(ies) preserved, <Q> note(s) held back for your review.`
```

Render tasks in ascending numeric order, then the `Ungrouped` section, then the single `Final cleanup` task. Omit the `Ungrouped` section entirely if `K == 0`. Always emit all three per-task steps even if a step is a no-op (e.g. "Step 1 — Implement: no code change; out of scope per your direction") — the executor relies on the fixed shape. Always emit the `Final cleanup` task, even if every thread's note list is empty (then it is a no-op that confirms nothing pre-plan remains).

## Plan completeness checklist

The executor operates from the plan alone, so every plan must carry — see the Phases above for the *how*; this is the closing checklist of *what must be present*:

- Per thread: `discussion_id` + first `note_id` as raw IDs (the executor calls delete/post endpoints with them, not permalinks).
- Per thread: **every** `@<plan_user>` note with `created_at <= plan_emit_time` as a baseline reference (`note_id` + permalink + **verbatim** body) — the full pre-plan set, not just numbered notes (an un-numbered `also handle nulls` counts). Verbatim, because cleanup deletes the note and the plan becomes its only record.
- Per thread: the **atomic reviewer asks** — one bullet per distinct request, since Step 2 checks each separately.
- Header: `plan_emit_time` (note cutoff) and `base_sha` (commit gate), plus `project_path`, `iid`, and `source_branch`.

## Parsing rules — quick reference

| Reply body (after trim) | Group | Direction text | Deleted in Final cleanup? |
|---|---|---|---|
| `1` | 1 | (empty) | yes (pre-plan) |
| `1.` | 1 | (empty) | yes (pre-plan) |
| `1 use a CTE here` | 1 | `use a CTE here` | yes (pre-plan) |
| `(2) split into two models` | 2 | `split into two models` | yes (pre-plan) |
| `#3 ignore — out of scope` | 3 | `ignore — out of scope` | yes (pre-plan) |
| `4: rename to active_time` | 4 | `rename to active_time` | yes (pre-plan) |
| `also handle nulls` (un-numbered follow-up) | none (inherits thread's latest number) | `also handle nulls` | yes (pre-plan — collect the ID anyway) |
| `agree, will rename` | none | `agree, will rename` | **hold for review** (free-form — fails marker test 1 and canonical test 2) |
| (no reply) | none | (none) | n/a |
| `Resolved in abc1234: …` left by a **prior run** (created ≤ plan_emit_time) | none | (empty — canonical shape, not direction) | **yes** (deleted via guard test 2; Step 3 re-posts a fresh equivalent) |
| `Resolved in abc1234: …` posted **this run** (created > plan_emit_time) | n/a | n/a | **no** — after the cutoff; this is the reply to keep |

## Edge cases

- **Reviewer self-replied to their own thread before you did** — ignore their follow-ups; only your notes affect grouping.
- **You replied multiple times, numbered differently each time** — latest numbered note wins; surface the earlier number in the direction text so it isn't lost (e.g. `(was 2, now 1) …`). All of those notes are pre-plan, so all are collected for Final cleanup.
- **Discussion on a file that has since been deleted in a later push** — still include it; mark the file path with a `(stale)` suffix.
- **MR has draft notes** (only visible to author) — `glab` and MCP both expose these; treat them like regular notes when matching your username.
- **Multiple reviewers in one thread** — credit the first non-system note's author as the reviewer; mention subsequent reviewer authors inline if their bodies add new asks.
- **`glab auth status` fails on this host** — fall back to MCP silently; do not surface the auth error unless MCP also fails.
- **Duplicate resolution comments already in the thread** from a prior run (the case the user reported: two identical `Broken onto one property per line in commit …` notes from `@<plan_user>` posted seconds apart). They were created before this plan, so they fall inside the `created_at <= plan_emit_time` cutoff and are deleted by Final cleanup — record them (id + permalink + verbatim body) under "Your baseline notes". The fresh Step 3 reply (posted after the cutoff) is the one that survives.
- **Reviewer's comment contains multiple distinct asks** ("rename X and add a comment"). Split into separate bullets under `Reviewer asks (atomic)` — each becomes its own validation check in Step 2. Aggregating them lets a half-done implementation pass validation.
- **One task spans multiple reviewer threads** (your number reply grouped them). Collect IDs and atomic asks for every thread under the same task; Step 2 must check each thread independently, and Final cleanup deletes each thread's pre-plan notes.
- **Thread is already `resolved=true` when planning runs.** It is out of scope: not fetched (Phase 2), not planned, and Final cleanup never deletes its notes. Comments under resolved threads are preserved unconditionally. If the user explicitly asks to re-open and rework such a thread, that is a fresh request — do not silently pull resolved threads into the plan or delete their comments.
- **No pre-plan notes in a thread** (e.g. an ungrouped item where the user never replied). The thread's "Your baseline notes" reads `(none)` and Final cleanup is a no-op for it — still list it.
- **A pre-plan `@<plan_user>` note is a real reviewer-facing reply, not an instruction marker** — the Final cleanup guard holds it back and asks the user rather than deleting, so a substantive comment is never lost to the timing rule.

## Common mistakes

| Mistake | Why it's wrong | Do instead |
|---|---|---|
| Including resolved discussions in plan | They've already been addressed; clutters the plan | Filter on `resolved == false` at fetch time |
| Hardcoding a username instead of resolving the MR assignee | The planning user varies per MR; a hardcoded name reads the wrong person's notes | Resolve `<plan_user>` from MR assignees each run (see [Determine the planning user](#determine-the-planning-user-the-assignee)) |
| Matching the git commit-author name instead of the GitLab username | They often differ (e.g. `janedoe` vs `jane.doe`); matching the author misses every reply | Always match on the GitLab `username` from the API |
| Silently picking one of several assignees | Guessing whose notes are instructions corrupts the plan | When 2+ assignees, ask once via `AskUserQuestion` which one is the planning user |
| Skipping ungrouped threads | They are still real work | List them under `Ungrouped`, sorted by file:line |
| Writing the plan to a file | User asked for chat-only output | Print to chat; let the next turn read it from context |
| Calling any GitLab write endpoint from this skill | The skill is read-only by design; the next-turn executor performs writes | Encode every write as a step in the plan, not an action here |
| Emitting a task without `discussion_id` / note IDs / atomic asks | Executor can't call delete/post endpoints or validate per-ask without them | Always collect raw IDs and split multi-ask reviewer bodies into bullets |
| Collecting only numbered notes for deletion | Un-numbered follow-up instructions then survive cleanup — the bug the user hit | Collect **every** `@<plan_user>` note with `created_at <= plan_emit_time`, numbered or not |
| Deleting notes per-task before posting | Two overlapping deletion mechanisms; risks wiping a note a later task still needs | Defer all deletion to the single Final cleanup task that runs after every Step 3 |
| Deleting a note created after plan_emit_time | That is a resolution reply this run just posted — the one thing to keep | Cutoff is strict: delete only `created_at <= plan_emit_time` |
| Aggregating multiple reviewer asks into one validation check | A half-done implementation passes | Split each ask into its own bullet under `Reviewer asks (atomic)` so Step 2 checks each one |
| Omitting a step when it is a no-op | Executor relies on the fixed 3-step shape plus Final cleanup | Emit the step with explicit "no-op" wording (e.g. "no baseline notes to delete") |
| Deleting comments under an already-resolved thread | Resolved threads are out of scope; their comments must be preserved | Filter them out at Phase 2; Final cleanup never touches a `resolved == true` thread |
| Putting "Post resolution" before "Validate" | Encourages the executor to post a misleading "Resolved" comment when the code didn't land | Keep the order Implement → Validate → Post resolution; Step 2 is the gate that decides whether Step 3 runs |
| Treating an unnumbered reply as group 0 | `0` is a valid user-chosen group | Ungrouped means "no number detected", not "group zero" |

## Keywords (for retrieval)

GitLab MR, merge request review, reviewer comments, non-resolved discussions, review plan, code review tasks, address review feedback, post resolution reply, delete original comments, final cleanup, clear old notes, pre-plan notes, baseline reference, preserve resolution replies, preserve resolved threads, cleanup instruction notes, verify reviewer comment addressed, glab CLI, GitLab MCP, planning user, MR assignee, resolve assignee, multiple assignees, atomic task grouping.
