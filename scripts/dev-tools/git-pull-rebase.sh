#!/usr/bin/env bash
#
# git-pull-rebase.sh
# Usage: ./git-pull-rebase.sh "Your commit message"
#
# Rebases onto local.

set -e  # exit on any error

# ----  Pull with rebase & autostash ----------------------------------------
echo "🔄  Running: git pull --rebase --autostash origin main"
git pull --rebase --autostash origin main

echo "✅  Done! Local branch is now up-to-date wit

