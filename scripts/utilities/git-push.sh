#!/usr/bin/env bash
#
# git-save.sh
# Usage: ./git-save.sh "Your commit message"
#
# Adds, commits, and pushes onto origin/main.

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

echo "✅  Done! Local branch is now up-to-date wit

