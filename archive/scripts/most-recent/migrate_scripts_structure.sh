#!/bin/bash
# Script: migrate_scripts_structure.sh
# Purpose: Safely migrate scripts to new directory structure
# Usage: ./migrate_scripts_structure.sh [--dry-run|--execute|--rollback]
# Dependencies: None
# Author: Claude & User
# Date: August 30, 2025
# Status: Active
# Notes: Run with --dry-run first to preview changes

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Mode selection
MODE="${1:---help}"

# Backup directory
BACKUP_DIR="${SCRIPT_DIR}/.backup_$(date +%Y%m%d_%H%M%S)"

# Files to move to active/
ACTIVE_FILES=(
    "ebnf_to_openapi_dynamic_v3.py"
    "add_tests.js"
    "fix_collection_urls_v2.py"
    "validate_collection.js"
    "fix_request_urls.py"
    "add_tests_jwt.js"
    "add_collection_variables.js"
    "fix-template-banner.sh"
)

# Files to move to utilities/
UTILITY_FILES=(
    "prism_test.sh"
    "generate-sdk.sh"
    "deploy-docs.sh"
    "git-pull-rebase.sh"
    "git-push.sh"
    "cleanup-scripts-directory.sh"
    "cleanup-openapi-directory.sh"
    "cleanup-docs-directory.sh"
    "generate_test_data.py"
    "verify_urls.py"
)

# Files to move to archived/
ARCHIVED_FILES=(
    "ebnf_to_openapi_grammer_based.py"
    "fix_collection_urls.py"
    "generate_openapi_from_swagger.py"
    "merge_yaml_files.py"
)

# Function to print colored messages
print_color() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Function to check if file exists
check_file() {
    local file=$1
    if [[ -f "${SCRIPT_DIR}/${file}" ]]; then
        return 0
    else
        print_color $YELLOW "Warning: File not found: ${file}"
        return 1
    fi
}

# Function to create Makefile patch
create_makefile_patch() {
    cat > "${SCRIPT_DIR}/makefile_updates.patch" << 'EOF'
# Makefile updates needed for new script structure
# Apply these changes to the Makefile after migration

# Update script references to use new paths:

# Active scripts (used in pipeline)
EBNF_TO_OPENAPI_SCRIPT := $(SCRIPTS_DIR)/active/ebnf_to_openapi_dynamic_v3.py
ADD_TESTS_SCRIPT := $(SCRIPTS_DIR)/active/add_tests.js
FIX_COLLECTION_URLS := $(SCRIPTS_DIR)/active/fix_collection_urls_v2.py
POSTMAN_VALIDATOR := $(SCRIPTS_DIR)/active/validate_collection.js

# Utility scripts (manual use)
PRISM_TEST_SCRIPT := $(SCRIPTS_DIR)/utilities/prism_test.sh
GENERATE_SDK_SCRIPT := $(SCRIPTS_DIR)/utilities/generate-sdk.sh
DEPLOY_DOCS_SCRIPT := $(SCRIPTS_DIR)/utilities/deploy-docs.sh

# Also update hardcoded paths:
# Line 984: node scripts/add_tests_jwt.js
# Change to: node $(SCRIPTS_DIR)/active/add_tests_jwt.js

# Line 1571: -f scripts/env_template.jq  
# Change to: -f $(SCRIPTS_DIR)/jq/env_template.jq
EOF
    print_color $GREEN "Created Makefile patch file: makefile_updates.patch"
}

# Dry run mode
dry_run() {
    print_color $GREEN "=== DRY RUN MODE ==="
    echo "This will show what would be done without making changes."
    echo ""
    
    print_color $YELLOW "Files to move to active/:"
    for file in "${ACTIVE_FILES[@]}"; do
        if check_file "$file"; then
            echo "  ✓ $file → active/$file"
        fi
    done
    echo ""
    
    print_color $YELLOW "Files to move to utilities/:"
    for file in "${UTILITY_FILES[@]}"; do
        if check_file "$file"; then
            echo "  ✓ $file → utilities/$file"
        fi
    done
    echo ""
    
    print_color $YELLOW "Files to move to archived/:"
    for file in "${ARCHIVED_FILES[@]}"; do
        if check_file "$file"; then
            echo "  ✓ $file → archived/$file"
        fi
    done
    echo ""
    
    print_color $GREEN "Makefile updates needed:"
    echo "  - Update EBNF_TO_OPENAPI_SCRIPT path"
    echo "  - Update ADD_TESTS_SCRIPT path"
    echo "  - Update other script variables"
    echo "  - Fix 2 hardcoded script paths"
    echo ""
    
    create_makefile_patch
}

# Execute migration
execute() {
    print_color $GREEN "=== EXECUTE MODE ==="
    
    # Create backup
    print_color $YELLOW "Creating backup..."
    mkdir -p "$BACKUP_DIR"
    cp -r "${SCRIPT_DIR}"/* "$BACKUP_DIR/" 2>/dev/null || true
    print_color $GREEN "Backup created at: $BACKUP_DIR"
    echo ""
    
    # Move files to active/
    print_color $YELLOW "Moving files to active/..."
    for file in "${ACTIVE_FILES[@]}"; do
        if check_file "$file"; then
            mv "${SCRIPT_DIR}/${file}" "${SCRIPT_DIR}/active/${file}"
            print_color $GREEN "  ✓ Moved $file → active/$file"
        fi
    done
    echo ""
    
    # Move files to utilities/
    print_color $YELLOW "Moving files to utilities/..."
    for file in "${UTILITY_FILES[@]}"; do
        if check_file "$file"; then
            mv "${SCRIPT_DIR}/${file}" "${SCRIPT_DIR}/utilities/${file}"
            print_color $GREEN "  ✓ Moved $file → utilities/$file"
        fi
    done
    echo ""
    
    # Move files to archived/
    print_color $YELLOW "Moving files to archived/..."
    for file in "${ARCHIVED_FILES[@]}"; do
        if check_file "$file"; then
            mv "${SCRIPT_DIR}/${file}" "${SCRIPT_DIR}/archived/${file}"
            print_color $GREEN "  ✓ Moved $file → archived/$file"
        fi
    done
    echo ""
    
    create_makefile_patch
    
    print_color $GREEN "=== MIGRATION COMPLETE ==="
    print_color $YELLOW "IMPORTANT NEXT STEPS:"
    echo "1. Review makefile_updates.patch"
    echo "2. Update the Makefile with the new paths"
    echo "3. Run 'make smart-rebuild-clean' to clear build hashes"
    echo "4. Test the entire pipeline with 'make smart-rebuild'"
    echo "5. If issues occur, run: $0 --rollback"
}

# Rollback function
rollback() {
    print_color $RED "=== ROLLBACK MODE ==="
    
    # Find most recent backup
    LATEST_BACKUP=$(ls -dt ${SCRIPT_DIR}/.backup_* 2>/dev/null | head -1)
    
    if [[ -z "$LATEST_BACKUP" ]]; then
        print_color $RED "Error: No backup found to rollback"
        exit 1
    fi
    
    print_color $YELLOW "Found backup: $LATEST_BACKUP"
    read -p "Restore from this backup? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Move files back from subdirectories
        for subdir in active utilities archived; do
            if [[ -d "${SCRIPT_DIR}/${subdir}" ]]; then
                mv "${SCRIPT_DIR}/${subdir}"/* "${SCRIPT_DIR}/" 2>/dev/null || true
            fi
        done
        
        print_color $GREEN "Files moved back to scripts/ root"
        print_color $YELLOW "Note: You'll need to manually revert Makefile changes"
    else
        print_color $YELLOW "Rollback cancelled"
    fi
}

# Help message
show_help() {
    cat << EOF
Script Migration Tool for C2M API Scripts Directory

Usage: $0 [option]

Options:
    --dry-run    Preview what would be done without making changes
    --execute    Perform the actual migration (creates backup first)
    --rollback   Restore files to original locations from backup
    --help       Show this help message

Example:
    $0 --dry-run     # See what would happen
    $0 --execute     # Perform migration
    $0 --rollback    # Undo migration

This script reorganizes the scripts/ directory into:
    - active/     Scripts used by Makefile
    - utilities/  Useful manual scripts
    - archived/   Legacy/deprecated scripts
EOF
}

# Main execution
case "$MODE" in
    --dry-run)
        dry_run
        ;;
    --execute)
        print_color $RED "WARNING: This will reorganize the scripts directory!"
        read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            execute
        else
            print_color $YELLOW "Migration cancelled"
        fi
        ;;
    --rollback)
        rollback
        ;;
    --help|*)
        show_help
        ;;
esac