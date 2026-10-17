#!/usr/bin/env bash
#
# git-pull-rebase.sh
# Usage: ./scripts/dev-tools/git-pull-rebase.sh [branch]      (make git-pull-rebase)
#
# Pulls the current (or given) branch with rebase + autostash from the remote that
# .git-context selects — personal -> origin (faserrao), click2mail -> click2mail — the same
# mapping git-push.sh / 'git ctx-push' use for pushing.

set -euo pipefail

CONTEXT=$(cat .git-context 2>/dev/null || echo "personal")
case "$CONTEXT" in
  personal)              REMOTE=origin ;;
  click2mail|corporate)  REMOTE=click2mail ;;
  *) echo "❌  Unknown context in .git-context: $CONTEXT (expected personal or click2mail)"; exit 1 ;;
esac
BRANCH="${1:-$(git rev-parse --abbrev-ref HEAD)}"

echo "🔄  Running: git pull --rebase --autostash $REMOTE $BRANCH  (context: $CONTEXT)"
git pull --rebase --autostash "$REMOTE" "$BRANCH"

echo "✅  Done! $BRANCH is up to date with $REMOTE/$BRANCH."
