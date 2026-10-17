#!/usr/bin/env bash
#
# git-push.sh
# Usage: ./git-push.sh "Your commit message"
#
# Adds, commits, and pushes the current branch to the remote selected by
# .git-context (personal -> faserrao, click2mail -> click2mail) using the
# 'git ctx-push' alias. This keeps pushes consistent with the Postman
# workspace/API-key context the build uses.

set -e  # exit on any error

# ---- 1. Check for commit message -------------------------------------------
if [[ -z "$1" ]]; then
  echo "❌  Commit message required."
  echo "Usage: $0 \"Your commit message\""
  exit 1
fi
COMMIT_MSG="$1"

# ---- 2. Stage everything ----------------------------------------------------
echo "➕  Running: git add ."
git add .

# ---- 3. Commit --------------------------------------------------------------
echo "📝  Running: git commit -m \"$COMMIT_MSG\""
git commit -m "$COMMIT_MSG"

# ---- 4. Push (context-aware) ------------------------------------------------
BRANCH=$(git rev-parse --abbrev-ref HEAD)
CONTEXT=$(git ctx-show)
echo "🚀  Running: git ctx-push \"$BRANCH\"  (context: $CONTEXT)"
git ctx-push "$BRANCH"

echo "✅  Done! Pushed $BRANCH to the '$CONTEXT' remote (triggers its GitHub Actions workflow)."
