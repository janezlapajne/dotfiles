#!/usr/bin/env bash
set -euo pipefail

WORKTREE="${1:?Usage: setup-farming-data-layer.sh <worktree_path>}"
TOOLS="$WORKTREE/tools"
LOGDIR="$(cd "$(git -C "$WORKTREE" rev-parse --git-common-dir)" && pwd)/wt-logs"
LOGFILE="$LOGDIR/setup-farming-data-layer.log"
ENV_SRC="$HOME/.config/worktrunk/farming-data-layer.env"

mkdir -p "$LOGDIR"
exec > >(tee "$LOGFILE") 2>&1

echo "==> Setting up worktree: $WORKTREE"

if [ ! -f "$ENV_SRC" ]; then
    echo "ERROR: .env file not found at $ENV_SRC"
    echo "Please create it before running this script."
    echo "It should contain the environment variables needed by farming-data-layer."
    exit 1
fi

echo "==> Copying .env..."
cp "$ENV_SRC" "$TOOLS/.env"

# settings.local.json is gitignored, so it doesn't follow the worktree checkout —
# symlink to the primary so Claude permission changes are shared across worktrees.
PRIMARY="$(git -C "$WORKTREE" worktree list --porcelain | awk '/^worktree / {print $2; exit}')"
SETTINGS_SRC="$PRIMARY/.claude/settings.local.json"
if [ -f "$SETTINGS_SRC" ] && [ "$PRIMARY" != "$WORKTREE" ]; then
    echo "==> Linking .claude/settings.local.json -> $SETTINGS_SRC"
    mkdir -p "$WORKTREE/.claude"
    ln -sfn "$SETTINGS_SRC" "$WORKTREE/.claude/settings.local.json"
fi

# Apply any wtv-stashed per-branch vars to .env as UPPER_SNAKE keys, replacing
# any pre-existing line for the same key.
while IFS=$'\t' read -r key val; do
    [ -z "$key" ] && continue
    envkey="$(printf '%s' "$key" | tr 'a-z-' 'A-Z_')"
    sed -i.bak "/^${envkey}=/d" "$TOOLS/.env" && rm -f "$TOOLS/.env.bak"
    printf '%s=%s\n' "$envkey" "$val" >> "$TOOLS/.env"
    echo "==> override .env: ${envkey}=${val}"
done < <(wt -C "$WORKTREE" config state vars list 2>/dev/null)

unset VIRTUAL_ENV

echo "==> Installing dependencies..."
cd "$TOOLS" && uv sync 2>&1 | grep -E "^(Resolved|Installed|Audited)" || true

if [ ! -f project_configs.py ]; then
    echo "project_configs.py not found in this branch, skipping config setup"
    exit 0
fi

echo "==> Setting up symlinks..."
uv run project_configs.py vscode symlink --target root --yolo --force
uv run project_configs.py claude symlink --target root --yolo --force
uv run project_configs.py skills symlink --target root --agent claude --yolo --force
uv run project_configs.py dbt copy --yolo --force --no-backup

echo "==> Refresh env..."
just bq_reset_env --yolo


echo "==> Done! Worktree ready: $WORKTREE"
