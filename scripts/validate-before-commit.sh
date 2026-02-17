#!/bin/bash
# validate-before-commit.sh
# Validates EBNF syntax before committing changes
# Usage: ./scripts/validate-before-commit.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}=== EBNF Pre-Commit Validation ===${NC}"
echo ""

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Check if EBNF file exists
EBNF_FILE="data_dictionary/c2mapiv2-dd.ebnf"
if [ ! -f "$EBNF_FILE" ]; then
    echo -e "${RED}ERROR: EBNF file not found: $EBNF_FILE${NC}"
    exit 1
fi

# Check if Python venv exists
PYTHON_VENV="scripts/python_env/e2o.venv/bin/python"
if [ ! -f "$PYTHON_VENV" ]; then
    echo -e "${RED}ERROR: Python virtual environment not found${NC}"
    echo "Run: make install"
    exit 1
fi

# Step 1: Validate EBNF syntax
echo -e "${BLUE}Step 1: Validating EBNF syntax...${NC}"
TRANSLATOR="scripts/active/ebnf_to_openapi_dynamic_v3.py"

# Run translator with --report flag to check for parse errors
if ! $PYTHON_VENV $TRANSLATOR --report $EBNF_FILE > /tmp/ebnf_report.txt 2>&1; then
    echo -e "${RED}EBNF VALIDATION FAILED${NC}"
    echo ""
    cat /tmp/ebnf_report.txt
    echo ""
    echo -e "${YELLOW}Fix the errors above before committing.${NC}"
    exit 1
fi

# Check for 0 productions (indicates complete parse failure)
PRODUCTIONS=$(grep "productions parsed" /tmp/ebnf_report.txt | awk '{print $1}')
if [ "$PRODUCTIONS" = "0" ]; then
    echo -e "${RED}CRITICAL: 0 productions parsed${NC}"
    echo ""
    cat /tmp/ebnf_report.txt
    echo ""
    echo -e "${YELLOW}This usually means a syntax error in EBNF.${NC}"
    echo "Common issues:"
    echo "  - Dictionary syntax { string : string } (not supported)"
    echo "  - Missing semicolon at end of definition"
    echo "  - Unmatched parentheses in comments"
    exit 1
fi

echo -e "${GREEN}✓ EBNF syntax valid${NC}"
echo "  Productions parsed: $PRODUCTIONS"

# Step 2: Check for duplicate definitions
echo ""
echo -e "${BLUE}Step 2: Checking for duplicate definitions...${NC}"

# Extract all definition names (lines matching "identifier =")
DEFINITIONS=$(grep -E "^[a-zA-Z][a-zA-Z0-9_]* =" $EBNF_FILE | awk '{print $1}' | sort)

# Check for duplicates
DUPLICATES=$(echo "$DEFINITIONS" | uniq -d)

if [ -n "$DUPLICATES" ]; then
    echo -e "${RED}DUPLICATE DEFINITIONS FOUND:${NC}"
    echo "$DUPLICATES"
    echo ""
    echo -e "${YELLOW}Each identifier should be defined only once.${NC}"
    echo "Search for duplicate definitions:"
    for dup in $DUPLICATES; do
        echo "  grep '^$dup =' $EBNF_FILE"
    done
    exit 1
fi

echo -e "${GREEN}✓ No duplicate definitions found${NC}"

# Step 3: Check for undefined references (basic check)
echo ""
echo -e "${BLUE}Step 3: Checking for common issues...${NC}"

# Check for commented definitions that might be referenced
COMMENTED_DEFS=$(grep -E "^\(\*.*[a-zA-Z][a-zA-Z0-9_]* =.*\*\)" $EBNF_FILE | wc -l | xargs)
if [ "$COMMENTED_DEFS" -gt 0 ]; then
    echo -e "${YELLOW}WARNING: Found $COMMENTED_DEFS commented-out definitions${NC}"
    echo "  Make sure these aren't referenced by active definitions"
fi

# Check for TODO or TBD markers
TODOS=$(grep -i "TODO\|TBD" $EBNF_FILE | wc -l | xargs)
if [ "$TODOS" -gt 0 ]; then
    echo -e "${YELLOW}NOTE: Found $TODOS TODO/TBD markers${NC}"
    echo "  These may need to be completed before production"
fi

echo -e "${GREEN}✓ Basic checks passed${NC}"

# Summary
echo ""
echo -e "${GREEN}=== VALIDATION COMPLETE ===${NC}"
echo -e "${GREEN}✓ EBNF syntax is valid${NC}"
echo -e "${GREEN}✓ No duplicate definitions${NC}"
echo -e "${GREEN}✓ Safe to commit!${NC}"
echo ""
echo "Next steps:"
echo "  1. Preview changes:  ./scripts/preview-ebnf-changes.sh"
echo "  2. Test build:       make postman-instance-build-without-tests"
echo "  3. Commit & push:    git add . && git commit && git push"
echo ""

exit 0
