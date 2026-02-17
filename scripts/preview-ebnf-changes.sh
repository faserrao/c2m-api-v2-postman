#!/bin/bash
# preview-ebnf-changes.sh
# Shows what will change in OpenAPI spec after EBNF modifications
# Usage: ./scripts/preview-ebnf-changes.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}=== Preview EBNF Changes ===${NC}"
echo ""

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check if there are uncommitted EBNF changes
if ! git diff --quiet data_dictionary/c2mapiv2-dd.ebnf; then
    echo -e "${GREEN}✓ Found uncommitted EBNF changes${NC}"
else
    echo -e "${YELLOW}WARNING: No uncommitted changes to EBNF file${NC}"
    echo "This will show what's different from the last commit."
    echo ""
fi

# Step 1: Backup current OpenAPI spec
echo -e "${BLUE}Step 1: Backing up current OpenAPI spec...${NC}"
OPENAPI_FILE="openapi/c2mapiv2-openapi-spec-base.yaml"

if [ -f "$OPENAPI_FILE" ]; then
    cp "$OPENAPI_FILE" "/tmp/openapi-spec-before.yaml"
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo -e "${YELLOW}No existing OpenAPI spec found (first generation)${NC}"
    touch "/tmp/openapi-spec-before.yaml"
fi

# Step 2: Generate new OpenAPI spec from current EBNF
echo ""
echo -e "${BLUE}Step 2: Generating OpenAPI spec from current EBNF...${NC}"

if ! make generate-openapi-spec-from-ebnf-dd > /tmp/openapi-generate.log 2>&1; then
    echo -e "${RED}ERROR: OpenAPI generation failed${NC}"
    echo ""
    cat /tmp/openapi-generate.log
    exit 1
fi

echo -e "${GREEN}✓ OpenAPI spec generated${NC}"

# Step 3: Show summary statistics
echo ""
echo -e "${BLUE}Step 3: Change summary${NC}"
echo ""

# Count changes
LINES_ADDED=$(git diff "$OPENAPI_FILE" | grep "^+" | grep -v "^+++" | wc -l | xargs)
LINES_REMOVED=$(git diff "$OPENAPI_FILE" | grep "^-" | grep -v "^---" | wc -l | xargs)
LINES_CHANGED=$((LINES_ADDED + LINES_REMOVED))

if [ "$LINES_CHANGED" -eq 0 ]; then
    echo -e "${YELLOW}No changes detected in OpenAPI spec${NC}"
    echo "Your EBNF changes may not have affected the generated spec."
    echo ""
    exit 0
fi

echo -e "Lines added:   ${GREEN}+$LINES_ADDED${NC}"
echo -e "Lines removed: ${RED}-$LINES_REMOVED${NC}"
echo -e "Total changes: $LINES_CHANGED lines"
echo ""

# Show file-level stats
git diff --stat "$OPENAPI_FILE"

# Step 4: Show detailed changes
echo ""
echo -e "${BLUE}Step 4: Detailed changes (first 100 lines)${NC}"
echo ""
echo -e "${YELLOW}-------------------------------------------${NC}"

# Show first 100 lines of diff with color
git diff "$OPENAPI_FILE" | head -100

# Check if there are more lines
TOTAL_DIFF_LINES=$(git diff "$OPENAPI_FILE" | wc -l | xargs)
if [ "$TOTAL_DIFF_LINES" -gt 100 ]; then
    echo ""
    echo -e "${YELLOW}... and $((TOTAL_DIFF_LINES - 100)) more lines${NC}"
    echo ""
    echo "View full diff? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        git diff "$OPENAPI_FILE" | less -R
    fi
fi

# Step 5: Check for breaking changes
echo ""
echo -e "${BLUE}Step 5: Checking for potential breaking changes...${NC}"
echo ""

BREAKING=false

# Check for removed endpoints
REMOVED_PATHS=$(git diff "$OPENAPI_FILE" | grep "^-  /" | grep -v "^---" | wc -l | xargs)
if [ "$REMOVED_PATHS" -gt 0 ]; then
    echo -e "${RED}WARNING: $REMOVED_PATHS endpoint(s) removed${NC}"
    git diff "$OPENAPI_FILE" | grep "^-  /" | grep -v "^---"
    BREAKING=true
fi

# Check for removed required fields
REMOVED_REQUIRED=$(git diff "$OPENAPI_FILE" | grep -A2 "^-.*required:" | wc -l | xargs)
if [ "$REMOVED_REQUIRED" -gt 0 ]; then
    echo -e "${RED}WARNING: Changes to required fields detected${NC}"
    BREAKING=true
fi

# Check for removed schemas
REMOVED_SCHEMAS=$(git diff "$OPENAPI_FILE" | grep "^-    [a-zA-Z].*:" | grep -v "^---" | wc -l | xargs)
if [ "$REMOVED_SCHEMAS" -gt 10 ]; then
    echo -e "${YELLOW}NOTE: $REMOVED_SCHEMAS schema properties removed/modified${NC}"
fi

if [ "$BREAKING" = true ]; then
    echo ""
    echo -e "${RED}⚠ BREAKING CHANGES DETECTED${NC}"
    echo "Review carefully before committing!"
else
    echo -e "${GREEN}✓ No obvious breaking changes detected${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}=== PREVIEW COMPLETE ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Review changes above"
echo "  2. Test locally:  make postman-instance-build-without-tests"
echo "  3. Commit:        git add data_dictionary/ openapi/"
echo "  4. Push:          git push origin main"
echo ""
echo "To revert OpenAPI changes without committing:"
echo "  git restore openapi/c2mapiv2-openapi-spec-base.yaml"
echo ""

exit 0
