#!/bin/bash

REPO_NAME="faserrao/c2m-api-repo"    # Change to your repo
USERNAME="faserrao"            	# Change to your GitHub username or org
PROJECT_TITLE="c2mApiV2"  # Change this to your GitHub Project title


# Build full repo identifier
REPO="$USERNAME/$REPO_NAME"

# === CHECKS ===
if [ ! -f "todos.txt" ]; then
  echo "❌ No todos.txt file found! Please create one with one task per line."
  exit 1
fi

# === CREATE ISSUES ===
while IFS= read -r task || [ -n "$task" ]; do
  if [ -n "$task" ]; then
    echo "➕ Creating issue: $task"
    gh issue create --repo "$REPO" --title "$task" --body "" --project "$PROJECT_TITLE"
  fi
done < todos.txt

echo "✅ All tasks have been added as issues in $REPO and linked to project '$PROJECT_TITLE'."
