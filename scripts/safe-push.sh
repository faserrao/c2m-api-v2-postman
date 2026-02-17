#!/bin/bash
# safe-push.sh
# Complete workflow: validate, build, preview, commit, and push
# Usage: ./scripts/safe-push.sh "Your commit message"

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}    C2M API V2 - Safe Push Workflow        ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check for commit message
if [ -z "$1" ]; then
    echo -e "${RED}ERROR: Commit message required${NC}"
    echo "Usage: ./scripts/safe-push.sh \"Your commit message\""
    exit 1
fi

COMMIT_MSG="$1"

# Check if there are any changes
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}No changes to commit${NC}"
    echo "Edit some files first!"
    exit 0
fi

# STEP 1: Validate EBNF
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 1: Validating EBNF Syntax${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

if ! ./scripts/validate-before-commit.sh; then
    echo ""
    echo -e "${RED}✗ VALIDATION FAILED${NC}"
    echo "Fix errors before pushing."
    exit 1
fi

# STEP 2: Generate OpenAPI spec
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 2: Generating OpenAPI Spec${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

if ! make generate-openapi-spec-from-ebnf-dd; then
    echo ""
    echo -e "${RED}✗ OpenAPI generation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ OpenAPI spec generated${NC}"

# STEP 3: Preview changes
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 3: Previewing Changes${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

./scripts/preview-ebnf-changes.sh || true  # Don't fail on diff errors

# STEP 4: Test build (optional but recommended)
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 4: Test Build (Optional)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""
echo "Run local build to test changes? (y/n)"
echo "(Takes ~8 minutes, but catches errors before CI/CD)"
read -r answer

if [ "$answer" = "y" ]; then
    echo ""
    echo "Running build..."
    if ! make postman-instance-build-without-tests; then
        echo ""
        echo -e "${RED}✗ Local build failed${NC}"
        echo "Fix errors before pushing."
        exit 1
    fi
    echo -e "${GREEN}✓ Local build successful${NC}"
else
    echo -e "${YELLOW}Skipping local build${NC}"
fi

# STEP 5: Show files to commit
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 5: Files to Commit${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

git status --short

# STEP 6: Confirm push
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 6: Ready to Commit and Push${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""
echo "Commit message: ${CYAN}$COMMIT_MSG${NC}"
echo ""
echo "This will:"
echo "  1. Stage data_dictionary/ and openapi/ files"
echo "  2. Commit with your message"
echo "  3. Push to origin main"
echo "  4. Trigger GitHub Actions workflow automatically"
echo ""
echo -e "${YELLOW}Proceed? (y/n)${NC}"
read -r answer

if [ "$answer" != "y" ]; then
    echo ""
    echo -e "${YELLOW}✗ Aborted. No changes pushed.${NC}"
    exit 0
fi

# STEP 7: Commit and push
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}STEP 7: Committing and Pushing${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# Stage changes
git add data_dictionary/ openapi/

# Commit
git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✓ Changes committed${NC}"

# Push
git push origin main
echo -e "${GREEN}✓ Pushed to GitHub${NC}"

# STEP 8: Success message
echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}           SUCCESS!                        ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "Your changes have been pushed to GitHub."
echo ""
echo "GitHub Actions workflow will now:"
echo "  1. Regenerate OpenAPI spec"
echo "  2. Generate Postman collections"
echo "  3. Publish to Postman workspace"
echo "  4. Deploy documentation"
echo "  5. Generate SDKs"
echo ""
echo "Monitor workflow progress:"
echo -e "${CYAN}https://github.com/click2mail/c2m-api-v2-postman/actions${NC}"
echo ""
echo "Expected completion time: ~3-4 minutes"
echo ""

exit 0
