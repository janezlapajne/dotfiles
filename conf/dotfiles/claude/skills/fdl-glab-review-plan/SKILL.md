---
name: fdl-glab-review-plan
description: Use when the user provides a GitLab merge request URL and wants an ordered, executable implementation plan derived from the open (non-resolved) reviewer discussions on that MR. The plan includes implement + cleanup + post-resolution + validation steps per task so a downstream execution skill can close each thread end-to-end. Triggered manually only.
disable-model-invocation: true
allowed-tools: Bash(glab:*), mcp__gitlab__whoami, mcp__gitlab__get_merge_request, mcp__gitlab__mr_discussions, mcp__gitlab__list_merge_request_notes, mcp__gitlab__get_merge_request_file_diff, mcp__gitlab__get_merge_request_diffs, Read, AskUserQuestion
---

# fdl-glab-review-plan

## Overview

Turns reviewer feedback on an open GitLab MR into an ordered task list a downstream execution skill can run. This skill is **read-only**: it inspects the MR, groups discussions, and emits a plan to chat. It never edits files and never writes to GitLab.

Reviewer discussions that the user (`@janez.lapajne`) has annotated in-thread with a leading number (e.g. `1`, `2.`, `(3)`) get grouped into one atomic task per number. Threads where the user gave a non-numbered reply — or no reply at all — become independent items at the end of the plan.

Each emitted task is self-contained and includes four steps in fixed order:

1. **Implement** — the concrete code change the downstream skill should make.
2. **Cleanup** — delete the user's numbering/instruction notes (`1`, `2 use CTE`, …) from every discussion this task covers, plus any duplicate resolution notes from prior runs (the case shown in the screenshot: two identical `@janez.lapajne` replies posted seconds apart).
3. **Validate (gate)** — explicit pass/fail checks confirming the change actually addresses every reviewer ask grouped into this task. If validation fails on a thread, the downstream skill must **skip Step 4 for that thread** and report the gap to the user instead of posting a misleading resolution.
4. **Post resolution** — a single reply added under each reviewer comment that passed Step 3, with the canonical `Resolved in <sha>: …` body.

The plan is the contract between this skill and the execution skill. Everything an executor needs to close the task should be on the page; nothing implicit.

## When to use

- User pastes a GitLab MR URL and asks for "the plan to address reviews", "review tasks", "let's start fixing comments", or similar.
- MR is in `opened` state and has non-resolved discussions.
- The intent is to *prepare* the work, not execute it. Execution happens in a following turn against the printed plan, run by a separate skill.

## When NOT to use

- MR is merged, closed, or has no open discussions → return a single-line summary instead.
- User wants to actually edit files now — let the downstream execution skill do that against the plan this skill emits. This skill never touches the repo.
- User wants this skill to delete notes / post replies on GitLab — it won't. The plan describes those steps; the execution skill performs them.

## Inputs

Required: GitLab MR URL.

If missing, ask **once** via `AskUserQuestion` with header `MR URL`, then stop if still missing. Accept both:
- `https://gitlab.com/<group>/<subgroup>/<project>/-/merge_requests/<iid>`
- Self-hosted equivalents on a different host.

Parse into `{host, project_path, mr_iid}`. URL-encode `project_path` when calling APIs.

## Hardcoded identity

The user is `@janez.lapajne` (note the dot — different from the git author `janezlapajne`). All "did the user reply?" checks compare discussion note `author.username == "janez.lapajne"`.

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

| Operation | `glab` | MCP fallback |
|---|---|---|
| MR metadata | `glab mr view <iid> -R <project_path> --output json` | `mcp__gitlab__get_merge_request` |
| Discussions | `glab api projects/<encoded>/merge_requests/<iid>/discussions --paginate` | `mcp__gitlab__mr_discussions` |
| File diff (optional context) | `glab mr diff <iid> -R <project_path>` | `mcp__gitlab__get_merge_request_file_diff` |

## Workflow

### Phase 1 — Validate

1. Parse the URL. If unparseable, ask once and stop on failure.
2. Probe tool selection (above).
3. Fetch MR metadata. If `state != "opened"`, print one line (`MR !<iid> is <state> — nothing to plan.`) and stop.

### Phase 2 — Fetch discussions

Pull every discussion on the MR (paginate). Keep only those where:
- The first note has `resolvable: true` AND `resolved: false`.
- The first note has `system: false` (skip "added 3 commits", "marked as draft", etc).

If zero discussions remain, print `No open discussions on MR !<iid>.` and stop.

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

Then walk the remaining notes in the discussion. For every note where `author.username == "janez.lapajne"`:
- Strip leading whitespace.
- **Group number** — match the first integer token using this regex (apply in order, first match wins):
  - `^#?\(?(\d+)\)?\s*[.)\-:]?\s*` — captures `1`, `1.`, `1)`, `(1)`, `#1`, `1 -`, `1:`
  - If a note's entire body is just a bare integer (after trim), that integer is the group.
  - No match → mark this note as ungrouped.
- **Direction text** — note body with the group-number prefix stripped. Empty if the whole reply was a digit.

If multiple user notes exist in the same thread:
- Group number: use the **latest** numbered note. If none of them are numbered, the thread is ungrouped.
- Direction text: concatenate all non-empty direction snippets in chronological order, separated by `; `.

### Phase 4 — Group into tasks

- Threads sharing a group number → one **Task N**.
- Threads without a group number (no reply, or unnumbered replies) → individual items under **Ungrouped**, sorted by `(file, line)` for stable ordering.

### Phase 5 — Emit the plan

Print to chat using the template below. No file write.

## Output template

Each task block contains four numbered steps in fixed order. The downstream execution skill MUST run them in that order: Implement → Cleanup → Validate → Post resolution. Step 3 is the gate — when validation fails for a thread, Step 4 MUST be skipped for that thread and the failure surfaced to the user.

```markdown
# Review adaptation plan — MR !<iid>: <title>

Source: `<source_branch>` → `<target_branch>` (head `<short_sha>`)
Project: `<project_path>`  •  MR IID: `<iid>`
Open discussions: <N>  •  Grouped tasks: <M>  •  Ungrouped: <K>

## Task <number> — <short summary derived from your direction>

**Your direction:** <concatenated direction text — verbatim, no rewording>

**Covers <n> reviewer thread(s):**
- @<reviewer> on `<file>`:<line> — "<first ~120 chars of reviewer body>…"
  Discussion ID: `<discussion_id>`  •  First note ID: `<note_id>`  •  Permalink: <permalink>
  Reviewer asks (atomic): <bullet list — one bullet per distinct ask in the reviewer's body; this is the validation checklist for step 4>
  Your instruction notes to delete: `<note_id_a>`, `<note_id_b>` (these are your `1` / `2 use CTE` markers — IDs only, no bodies)
- @<reviewer2> on `<file2>`:<line2> — "<…>"
  Discussion ID: `<discussion_id_2>`  •  First note ID: `<note_id_2>`  •  Permalink: <permalink_2>
  Reviewer asks (atomic): <…>
  Your instruction notes to delete: `<…>`

### Step 1 — Implement

<one or more concrete code-change actions derived from your direction; if direction is empty, derive from the reviewer's ask. Reference file:line and what the new code should look like at a sketch level.>

Commit message suggestion: `<short imperative line, e.g. "models: split STRUCT properties onto one per line">`

### Step 2 — Cleanup stale `@janez.lapajne` notes

For each discussion in this task:

- Delete every instruction note listed above by ID (the `1` / `2 use CTE` style markers).
- Inspect remaining `@janez.lapajne` notes in the thread. If two or more have the same whitespace-normalized body (duplicate resolution comments left over from prior runs — see screenshot reference), delete all of them; the fresh reply in Step 3 replaces them. If only one such note exists and Step 3 will post a fresh reply, delete it too.
- Never delete a note authored by anyone other than `janez.lapajne`. Never delete the reviewer's first note.
- A 404 on delete = already gone; keep going. A 403 = stop for that thread and surface to the user.

### Step 3 — Validate (gate before any posting)

For every discussion in this task, confirm each line below evaluates true. **If any check fails, do NOT proceed to Step 4 for that thread — skip the post and report the gap to the user instead.**

- [ ] Source branch has at least one new commit since the plan was emitted (`git log <source_branch> --since="<plan_emit_time>"` is non-empty), **or** the task's direction is explicitly "out of scope".
- [ ] Each `file:line` referenced by the covered discussions is touched by the new commit(s), **or** the reviewer's ask was file-level / structural and the file is still touched.
- [ ] Each bullet under "Reviewer asks (atomic)" above is semantically satisfied by the diff — verified item by item, not in aggregate. (E.g. reviewer asked "rename X and add a comment" → both the rename and the comment must be present.)
- [ ] No `@janez.lapajne` instruction note remains in any covered discussion (Step 2 should have ensured this; re-fetch and confirm).
- [ ] For threads where the reviewer has now marked `resolved=true` (someone else closed it while the task ran), mark the thread as "skip Step 4" and continue — not a failure, but no resolution post should be made.

Validation is per-thread, not per-task: if a task spans three threads and two pass while one fails, post resolutions on the two and report the gap on the third.

**If a thread fails validation**, emit a clearly-labelled block to chat (do not proceed to Step 4 for that thread):

```
⚠ Task <N> — validation failed on discussion <permalink>
- Reviewer ask not covered: <which bullet from the atomic list>
- What was checked: <commits inspected, files diffed>
- Why it didn't match: <one-sentence explanation>
- Action: re-implement or re-run after the missing change ships. Resolution NOT posted.
```

The user must see every unresolved item — do not silently swallow.

### Step 4 — Post resolution reply (only for threads that passed Step 3)

For each thread that passed Step 3 and is not already `resolved=true`, post exactly one reply, threaded under the reviewer's first note. Canonical body:

```
Resolved in <short_sha>: <one sentence on what changed and why it satisfies the reviewer's ask>. <optional: verification done — tests, manual run>.
```

- `<short_sha>` is the 7-char prefix of the implementing commit on `<source_branch>`. Multiple commits → comma-separate.
- "Won't do" outcomes use: `Out of scope: <reason captured in your direction>.` (no SHA).
- Never `@`-mention the reviewer; the reply already threads under their note.
- Before posting, re-check the thread: if a `@janez.lapajne` note with an identical (whitespace-normalized) body already exists (Step 2 should have removed it — this is a belt-and-braces check), skip the post and log `Resolution already present — skipped`.

After all Step 4 posts for the task succeed, emit a one-line per-task close summary to chat:
`Task <N> closed — <X> discussion(s) resolved, <I> instruction note(s) deleted, <Z> duplicate(s) cleaned, <S> skipped (see ⚠ blocks above).`

If any thread reached the close summary with a non-zero `<S>`, the task is **partially closed**, not closed. The user has the ⚠ blocks; they decide whether to re-run.

---

## Ungrouped — independent items

### U1 — @<reviewer> on `<file>`:<line>
Reviewer: "<short quote>"
Your reply: <verbatim, or "(no reply)">
Discussion ID: `<discussion_id>`  •  Permalink: <permalink>
Your instruction notes to delete: `<note_id>` (or "(none)")

Reviewer asks (atomic): <bullet list>

**Step 1 — Implement:** <…>
**Step 2 — Cleanup:** <delete instruction notes listed above + dedupe>
**Step 3 — Validate (gate):** <same checklist as Task block, scoped to this single thread; on failure emit ⚠ block and skip Step 4>
**Step 4 — Post resolution:** <canonical body sketch — only if Step 3 passed>
```

Render tasks in ascending numeric order, then the `Ungrouped` section. Omit the `Ungrouped` section entirely if `K == 0`. Always emit all four steps per task even if a step is a no-op (e.g. "Step 2 — Cleanup: no instruction notes to delete; check thread for duplicate resolution notes before Step 3") — the execution skill relies on the fixed shape.

## What this skill must collect for the plan to be executable

Because the execution skill operates from the plan alone, every task block must carry:

- `discussion_id` and first `note_id` for each covered thread (raw IDs, not just permalinks — the execution skill needs them to call delete/post endpoints).
- All `@janez.lapajne` note IDs in each thread that count as **instruction notes** (numbering markers, short TODO-to-self directions ≤ ~200 chars matching the numbering regex `^#?\(?(\d+)\)?\s*[.)\-:]?\s*` or a bare integer). List the IDs only — bodies stay in the API; the executor re-fetches.
- The **atomic reviewer asks** for each thread: split the reviewer's body into one bullet per distinct request. A single reviewer comment can carry multiple asks ("rename X and add a comment"); the validation step counts each separately, so each must appear as its own checklist item.
- The MR's `project_path` (URL-encoded form will be derived by the executor) and `iid`, and the `source_branch` so the executor can `git log` against it for validation.

## Parsing rules — quick reference

| Reply body (after trim) | Group | Direction text |
|---|---|---|
| `1` | 1 | (empty) |
| `1.` | 1 | (empty) |
| `1 use a CTE here` | 1 | `use a CTE here` |
| `(2) split into two models` | 2 | `split into two models` |
| `#3 ignore — out of scope` | 3 | `ignore — out of scope` |
| `4: rename to active_time` | 4 | `rename to active_time` |
| `agree, will rename` | none | `agree, will rename` |
| (no reply) | none | (none) |

## Edge cases

- **Reviewer self-replied to their own thread before you did** — ignore their follow-ups; only your notes affect grouping.
- **You replied multiple times, numbered differently each time** — latest numbered note wins; surface the earlier number in the direction text so it isn't lost (e.g. `(was 2, now 1) …`).
- **Discussion on a file that has since been deleted in a later push** — still include it; mark the file path with a `(stale)` suffix.
- **MR has draft notes** (only visible to author) — `glab` and MCP both expose these; treat them like regular notes when matching your username.
- **Multiple reviewers in one thread** — credit the first non-system note's author as the reviewer; mention subsequent reviewer authors inline if their bodies add new asks.
- **`glab auth status` fails on this host** — fall back to MCP silently; do not surface the auth error unless MCP also fails.
- **Duplicate resolution comments already in the thread** (the case shown by the user: two identical `Broken onto one property per line in commit …` notes from `@janez.lapajne` posted seconds apart). Surface them in the task block's `Your instruction notes to delete` / cleanup notes so the executor wipes them in Step 2 before posting a fresh reply.
- **Reviewer's comment contains multiple distinct asks** ("rename X and add a comment"). Split into separate bullets under `Reviewer asks (atomic)` — each becomes its own validation check in Step 4. Aggregating them lets a half-done implementation pass validation.
- **One task spans multiple reviewer threads** (your number reply grouped them). Collect IDs and atomic asks for every thread under the same task; Step 4 must check each thread independently.
- **Thread is already `resolved=true` when planning runs** but the user explicitly wants it included. Still emit the task but mark it `(already resolved)` and instruct Step 3 to skip the post; Step 2 can still delete leftover instruction notes.
- **No instruction notes to delete in a thread** (e.g. an ungrouped item where the user never replied). Step 2 becomes `no instruction notes to delete; check thread for duplicate resolution notes before Step 3` — still emit the step.

## Common mistakes

| Mistake | Why it's wrong | Do instead |
|---|---|---|
| Including resolved discussions in plan | They've already been addressed; clutters the plan | Filter on `resolved == false` at fetch time |
| Matching `janezlapajne` instead of `janez.lapajne` | That's the git author, not the GitLab username | Use the dotted form, always |
| Skipping ungrouped threads | They are still real work | List them under `Ungrouped`, sorted by file:line |
| Writing the plan to a file | User asked for chat-only output | Print to chat; let the next turn read it from context |
| Calling any GitLab write endpoint from this skill | The skill is read-only by design; the execution skill performs writes | Encode every write as a step in the plan, not an action here |
| Emitting a task without `discussion_id` / note IDs / atomic asks | Executor can't call delete/post endpoints or validate per-ask without them | Always collect raw IDs and split multi-ask reviewer bodies into bullets |
| Aggregating multiple reviewer asks into one validation check | A half-done implementation passes | Split each ask into its own bullet under `Reviewer asks (atomic)` so Step 4 checks each one |
| Omitting Step 2 or Step 4 when a step is a no-op | Executor relies on the fixed 4-step shape | Emit the step with explicit "no-op" wording (e.g. "no instruction notes to delete") |
| Putting "Post resolution" before "Validate" | Encourages the executor to post a misleading "Resolved" comment when the code didn't land | Keep the order Implement → Cleanup → Validate → Post resolution; Step 3 is the gate that decides whether Step 4 runs |
| Treating an unnumbered reply as group 0 | `0` is a valid user-chosen group | Ungrouped means "no number detected", not "group zero" |

## Keywords (for retrieval)

GitLab MR, merge request review, reviewer comments, non-resolved discussions, review plan, code review tasks, address review feedback, post resolution reply, delete duplicate comments, cleanup instruction notes, verify reviewer comment addressed, glab CLI, GitLab MCP, janez.lapajne, atomic task grouping.
