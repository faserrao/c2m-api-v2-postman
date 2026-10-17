#!/bin/bash
# =============================================================================
# Newman Test Execution Wrapper
# =============================================================================
# Purpose: Standardized wrapper for Newman test execution with reporting
# Author: Claude Code
# Date: 2025-11-04
# =============================================================================

set -eo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
COLLECTION=""
ENVIRONMENT=""
OUTPUT_DIR="reports"
REPORTERS="cli,html,json"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
VERBOSE=false

# Usage
usage() {
    cat << EOF
Newman Test Execution Wrapper
==============================

Usage:
    $(basename "$0") [options]

Options:
    -c, --collection PATH       Postman collection file path (required)
    -e, --environment PATH      Postman environment file path (required)
    -o, --output-dir DIR        Output directory for reports (default: reports)
    -r, --reporters LIST        Comma-separated list of reporters (default: cli,html,json)
    -v, --verbose               Enable verbose output
    -h, --help                  Show this help message

Reporters:
    cli                         Console output
    html                        HTML report
    json                        JSON report
    junit                       JUnit XML report

Examples:
    # Basic usage
    $(basename "$0") -c postman/collection.json -e postman/environment.json

    # Custom output directory and reporters
    $(basename "$0") -c collection.json -e env.json -o /tmp/reports -r cli,html,junit

Environment Variables:
    NEWMAN_OPTIONS              Additional Newman CLI options

EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--collection)
            COLLECTION="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -r|--reporters)
            REPORTERS="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Run '$(basename "$0") --help' for usage information"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$COLLECTION" ]]; then
    echo -e "${RED}❌ Error: Collection file is required${NC}"
    echo "Run '$(basename "$0") --help' for usage information"
    exit 1
fi

if [[ -z "$ENVIRONMENT" ]]; then
    echo -e "${RED}❌ Error: Environment file is required${NC}"
    echo "Run '$(basename "$0") --help' for usage information"
    exit 1
fi

# Validate files exist
if [[ ! -f "$COLLECTION" ]]; then
    echo -e "${RED}❌ Error: Collection file not found: $COLLECTION${NC}"
    exit 1
fi

if [[ ! -f "$ENVIRONMENT" ]]; then
    echo -e "${RED}❌ Error: Environment file not found: $ENVIRONMENT${NC}"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Extract collection name for report filenames
COLLECTION_NAME=$(basename "$COLLECTION" .json)

# Verbose output
if [[ "$VERBOSE" == "true" ]]; then
    echo -e "${BLUE}🔬 Newman Test Execution${NC}"
    echo "   Collection: $COLLECTION"
    echo "   Environment: $ENVIRONMENT"
    echo "   Output Directory: $OUTPUT_DIR"
    echo "   Reporters: $REPORTERS"
    echo "   Timestamp: $TIMESTAMP"
    echo ""
fi

# Build Newman command
NEWMAN_CMD="npx newman run \"$COLLECTION\""
NEWMAN_CMD="$NEWMAN_CMD -e \"$ENVIRONMENT\""
NEWMAN_CMD="$NEWMAN_CMD --reporters $REPORTERS"
NEWMAN_CMD="$NEWMAN_CMD --reporter-html-export \"$OUTPUT_DIR/newman-$COLLECTION_NAME-$TIMESTAMP.html\""
NEWMAN_CMD="$NEWMAN_CMD --reporter-json-export \"$OUTPUT_DIR/newman-$COLLECTION_NAME-$TIMESTAMP.json\""
NEWMAN_CMD="$NEWMAN_CMD --ignore-redirects"

# Add custom options from environment
if [[ -n "${NEWMAN_OPTIONS:-}" ]]; then
    NEWMAN_CMD="$NEWMAN_CMD $NEWMAN_OPTIONS"
fi

# Show command in verbose mode
if [[ "$VERBOSE" == "true" ]]; then
    echo -e "${BLUE}📋 Newman Command:${NC}"
    echo "   $NEWMAN_CMD"
    echo ""
fi

# Execute Newman
echo -e "${GREEN}🚀 Running Newman tests...${NC}"
echo ""

if eval "$NEWMAN_CMD"; then
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Newman tests passed${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Reports generated:"
    echo "   HTML: $OUTPUT_DIR/newman-$COLLECTION_NAME-$TIMESTAMP.html"
    echo "   JSON: $OUTPUT_DIR/newman-$COLLECTION_NAME-$TIMESTAMP.json"
    exit 0
else
    EXIT_CODE=$?
    echo ""
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}❌ Newman tests failed${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Reports generated:"
    echo "   HTML: $OUTPUT_DIR/newman-$COLLECTION_NAME-$TIMESTAMP.html"
    echo "   JSON: $OUTPUT_DIR/newman-$COLLECTION_NAME-$TIMESTAMP.json"
    echo ""
    echo "Review the reports for details on test failures."
    exit $EXIT_CODE
fi
