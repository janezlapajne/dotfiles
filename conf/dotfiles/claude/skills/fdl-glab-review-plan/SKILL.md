---
name: fdl-glab-review-plan
description: Use when the user provides a GitLab merge request URL and wants an ordered, executable implementation plan derived from the open (non-resolved) reviewer discussions on that MR. Triggered manually only.
disable-model-invocation: true
allowed-tools: Bash(glab:*), mcp__gitlab__whoami, mcp__gitlab__get_merge_request, mcp__gitlab__mr_discussions, mcp__gitlab__list_merge_request_notes, mcp__gitlab__get_merge_request_file_diff, mcp__gitlab__get_merge_request_diffs, Read, AskUserQuestion
---

# fdl-glab-review-plan

## Overview

Turns reviewer feedback on an open GitLab MR into an ordered task list a downstream Claude Code session can execute. Reviewer discussions that the user (`@janez.lapajne`) has annotated in-thread with a leading number (e.g. `1`, `2.`, `(3)`) get grouped into one atomic task per number. Threads where the user gave a non-numbered reply — or no reply at all — become independent items at the end of the plan. Output is printed to chat; nothing is written to disk and nothing is posted back to GitLab.

## When to use

- User pastes a GitLab MR URL and asks for "the plan to address reviews", "review tasks", "let's start fixing comments", or similar.
- MR is in `opened` state and has non-resolved discussions.
- The intent is to *prepare* the work, not execute it. Execution happens in a following turn against the printed plan.

## When NOT to use

- MR is merged, closed, or has no open discussions → return a single-line summary instead.
- User wants to *resolve* discussions on GitLab — this skill is read-only.
- User wants to actually edit files now — let the downstream session do that against the plan this skill emits.

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

```markdown
# Review adaptation plan — MR !<iid>: <title>

Source: `<source_branch>` → `<target_branch>` (head `<short_sha>`)
Open discussions: <N>  •  Grouped tasks: <M>  •  Ungrouped: <K>

## Task <number> — <short summary derived from your direction>

**Your direction:** <concatenated direction text>

**Covers <n> reviewer thread(s):**
- @<reviewer> on `<file>`:<line> — "<first ~120 chars of reviewer body>…"
  Discussion: <permalink>
- @<reviewer2> on `<file2>`:<line2> — "<…>"
  Discussion: <permalink>

**Suggested step:** <one concrete action — derived from your direction; if direction is empty, derive from the reviewer's ask>

---

## Ungrouped — independent items

### U1 — @<reviewer> on `<file>`:<line>
Reviewer: "<short quote>"
Your reply: <verbatim, or "(no reply)">
Discussion: <permalink>
**Suggested step:** <…>
```

Render tasks in ascending numeric order, then the `Ungrouped` section. Omit the `Ungrouped` section entirely if `K == 0`. Omit the per-task `Covers` block when a task wraps a single thread (use a single bullet line instead).

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

## Common mistakes

| Mistake | Why it's wrong | Do instead |
|---|---|---|
| Including resolved discussions | They've already been addressed; clutters the plan | Filter on `resolved == false` at fetch time |
| Matching `janezlapajne` instead of `janez.lapajne` | That's the git author, not the GitLab username | Use the dotted form, always |
| Skipping ungrouped threads | They are still real work | List them under `Ungrouped`, sorted by file:line |
| Writing the plan to a file | User asked for chat-only output | Print to chat; let the next turn read it from context |
| Posting suggestions back to GitLab | Skill is read-only by design | Do not call any write endpoints |
| Treating an unnumbered reply as group 0 | `0` is a valid user-chosen group | Ungrouped means "no number detected", not "group zero" |

## Keywords (for retrieval)

GitLab MR, merge request review, reviewer comments, non-resolved discussions, review plan, code review tasks, address review feedback, glab CLI, GitLab MCP, janez.lapajne, atomic task grouping.
