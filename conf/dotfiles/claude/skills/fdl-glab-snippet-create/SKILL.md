---
name: fdl-glab-snippet-create
description: Publish a markdown report as a GitLab project snippet in the farming-data-layer repo, following the fixed [FDL-REPORT] naming convention. Renders markdown (tables, code blocks) and returns a shareable URL for project members.
disable-model-invocation: true
allowed-tools: Bash(glab snippet create:*), Bash(date:*), Bash(git rev-parse:*), Read, Write, Edit
---

# fdl-glab-snippet-create

## Overview

Publish a markdown report as a GitLab **project snippet** in the farming-data-layer repo. GitLab renders the markdown (tables, code blocks) and `glab` returns a shareable URL that project members can open in a browser.

Every snippet follows one naming convention so they stay **filterable by kind and by date**.

> **Manual invocation only** — enforced by `disable-model-invocation: true` in the frontmatter. This skill is invoked only when the user explicitly runs `/fdl-glab-snippet-create`; Claude never auto-loads it.

## Naming convention (always apply, never improvise)

- **Title:** `[FDL-REPORT] <subject> — <YYYY-MM-DD>`
- **GitLab filename:** `fdl_report_<subject_snake>_<YYYY-MM-DD>.md`
- **Description:** `FDL report | <subject> | <YYYY-MM-DD>` (append ` | <extra keywords>` if useful, e.g. `fact_task`, `qa`, `analysis`)

Rules:
- `<YYYY-MM-DD>` is the **generation date** — get it with `date +%F`, never hardcode.
- `[FDL-REPORT]` is the umbrella tag for **every** snippet this skill creates — keep it verbatim so they all filter together.
- `<subject>` is a short human title (e.g. `fact_task negative metrics`); `<subject_snake>` is the same lowercased, spaces → underscores.

## Two modes

1. **From an existing markdown file** — the user provides the file path or name. Use it as-is. (Multiple files may be given.)
2. **Create, then publish** — the user gives content or instructions. Write the markdown file first (use the path the user indicates, or a sensible location of your choosing; create parent directories if needed), confirm it reads correctly, then publish.

## Workflow

1. `DATE=$(date +%F)` — resolve the real current date.
2. Resolve `<subject>` (ask, or infer from the file/topic) and derive `<subject_snake>`.
3. If in mode 2, Write the markdown file first.
4. Move to the repo root, then create the snippet (file paths are relative to the repo root; absolute paths are used as-is):
   ```bash
   cd "$(git rev-parse --show-toplevel)"
   glab snippet create \
     -t "[FDL-REPORT] <subject> — $DATE" \
     -v private \
     -f "fdl_report_<subject_snake>_$DATE.md" \
     -d "FDL report | <subject> | $DATE" \
     <path/to/file.md>
   ```
   Pass multiple file paths at the end to bundle several files into one snippet.
5. Return the printed URL to the user.

## Visibility

- Default **`private`** — for a *project* snippet this means visible to all **project members** (the team), not just you. This is the right default for team sharing here.
- **`internal` is blocked** by this instance's GitLab admin — using it fails with `403 ... Visibility level internal has been restricted`. Do not use it.
- Use `public` only if the user explicitly wants an unauthenticated link.

## Filtering later

Filter in the GitLab UI: **Project → Snippets**, then search `[FDL-REPORT]` (all skill-created snippets) or a date like `2026-06`.

> This `glab` version exposes only `snippet create` — `glab snippet list`/`view` silently fall back to help and do not work. Use the web UI (or the project Snippets page) to browse and filter.

## Common mistakes

- Hardcoding the date instead of `date +%F`.
- Using `-v internal` (admin-blocked — 403). Default to `private`.
- Dropping or altering the `[FDL-REPORT]` tag — breaks filtering.
- Passing multi-line markdown/SQL inline to `glab` — always pass a **file path**.
- Auto-running this skill because the user said "snippet" — it is manual-only.
