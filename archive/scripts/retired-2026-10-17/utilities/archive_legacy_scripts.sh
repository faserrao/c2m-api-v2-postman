#!/bin/bash
# Script: archive_legacy_scripts.sh
# Purpose: Archive legacy and unused scripts
# Usage: ./archive_legacy_scripts.sh [--dry-run|--execute]
# Dependencies: None
# Author: Claude & User
# Date: August 30, 2025
# Status: Active
# Notes: Archives scripts identified as legacy in UNUSED_SCRIPTS_ANALYSIS.md

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MODE="${1:---dry-run}"

# Legacy JQ scripts (replaced by versions in jq/ or integrated into Makefile)
LEGACY_JQ_SCRIPTS=(
    "add_testing_info_block.jq"  # Replaced by add_info.jq
    "add_tests.jq"               # Replaced by add_tests.js
    "create_env_payload.jq"      # Integrated into Makefile
    "create_mock_payload.jq"     # Integrated into Makefile
    "full_publish_payload.jq"    # Not used
    "link_env_to_mock_payload.jq" # Integrated into Makefile
    "link_payload.jq"            # Integrated into Makefile
    "postman_import_payload.jq"  # Integrated into Makefile
    "update_mock_env_payload.jq" # Integrated into Makefile
    "update_mock_payload.jq"     # Integrated into Makefile
    "update_payload.jq"          # Not used
    "url_hardfix_with_paths.jq" # Not used
    "verify_mock.jq"             # Not used
)

# Legacy Python scripts
LEGACY_PYTHON_SCRIPTS=(
    "ebnf_to_openapi_class_based.py"  # Replaced by dynamic_v3
    "analyze_endpoint_elements_v2.py"  # Analysis script, not used
    "extract_endpoint_ebnf_ordered.py" # Analysis script, not used
)

# Other legacy scripts
OTHER_LEGACY_SCRIPTS=(
    "generate-postman.sh"       # Replaced by Makefile targets
    "quick-validate.sh"         # Replaced by Makefile targets
    "inject-banner-correctly.js" # Not clear if used
    "merge-postman.js"          # May be useful, needs investigation
)

# Scripts that are used but in wrong location
MISPLACED_SCRIPTS=(
    "env_template.jq"           # Used by Makefile, should be in jq/
    "fix_paths.jq"              # Used by Makefile, should be in jq/
    "merge.jq"                  # Used by Makefile, should be in jq/
    "merge_overrides.jq"        # Used by Makefile, should be in jq/
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
        return 1
    fi
}

# Dry run mode
dry_run() {
    print_color $GREEN "=== DRY RUN MODE - Archive Legacy Scripts ==="
    echo ""
    
    print_color $YELLOW "Legacy JQ scripts to archive:"
    for script in "${LEGACY_JQ_SCRIPTS[@]}"; do
        if check_file "$script"; then
            echo "  ✓ $script → archived/$script"
        else
            echo "  ✗ $script (not found)"
        fi
    done
    echo ""
    
    print_color $YELLOW "Legacy Python scripts to archive:"
    for script in "${LEGACY_PYTHON_SCRIPTS[@]}"; do
        if check_file "$script"; then
            echo "  ✓ $script → archived/$script"
        else
            echo "  ✗ $script (not found)"
        fi
    done
    echo ""
    
    print_color $YELLOW "Other legacy scripts to archive:"
    for script in "${OTHER_LEGACY_SCRIPTS[@]}"; do
        if check_file "$script"; then
            echo "  ✓ $script → archived/$script"
        else
            echo "  ✗ $script (not found)"
        fi
    done
    echo ""
    
    print_color $BLUE "Misplaced scripts to move to jq/:"
    for script in "${MISPLACED_SCRIPTS[@]}"; do
        if check_file "$script"; then
            echo "  ✓ $script → jq/$script"
        else
            echo "  ✗ $script (not found)"
        fi
    done
    echo ""
    
    # Count totals
    local total_archive=0
    local total_move=0
    
    for script in "${LEGACY_JQ_SCRIPTS[@]}" "${LEGACY_PYTHON_SCRIPTS[@]}" "${OTHER_LEGACY_SCRIPTS[@]}"; do
        if check_file "$script"; then
            ((total_archive++))
        fi
    done
    
    for script in "${MISPLACED_SCRIPTS[@]}"; do
        if check_file "$script"; then
            ((total_move++))
        fi
    done
    
    print_color $GREEN "Summary:"
    echo "  - Scripts to archive: $total_archive"
    echo "  - Scripts to move to jq/: $total_move"
}

# Execute mode
execute() {
    print_color $GREEN "=== EXECUTE MODE - Archive Legacy Scripts ==="
    
    # Archive legacy JQ scripts
    print_color $YELLOW "Archiving legacy JQ scripts..."
    for script in "${LEGACY_JQ_SCRIPTS[@]}"; do
        if check_file "$script"; then
            mv "${SCRIPT_DIR}/${script}" "${SCRIPT_DIR}/archived/${script}"
            print_color $GREEN "  ✓ Archived $script"
        fi
    done
    echo ""
    
    # Archive legacy Python scripts
    print_color $YELLOW "Archiving legacy Python scripts..."
    for script in "${LEGACY_PYTHON_SCRIPTS[@]}"; do
        if check_file "$script"; then
            mv "${SCRIPT_DIR}/${script}" "${SCRIPT_DIR}/archived/${script}"
            print_color $GREEN "  ✓ Archived $script"
        fi
    done
    echo ""
    
    # Archive other legacy scripts
    print_color $YELLOW "Archiving other legacy scripts..."
    for script in "${OTHER_LEGACY_SCRIPTS[@]}"; do
        if check_file "$script"; then
            mv "${SCRIPT_DIR}/${script}" "${SCRIPT_DIR}/archived/${script}"
            print_color $GREEN "  ✓ Archived $script"
        fi
    done
    echo ""
    
    # Move misplaced scripts to jq/
    print_color $BLUE "Moving misplaced scripts to jq/..."
    for script in "${MISPLACED_SCRIPTS[@]}"; do
        if check_file "$script"; then
            mv "${SCRIPT_DIR}/${script}" "${SCRIPT_DIR}/jq/${script}"
            print_color $GREEN "  ✓ Moved $script to jq/"
        fi
    done
    echo ""
    
    # Create README in archived directory
    create_archived_readme
    
    print_color $GREEN "=== ARCHIVING COMPLETE ==="
}

# Create README for archived directory
create_archived_readme() {
    cat > "${SCRIPT_DIR}/archived/README.md" << 'EOF'
# Archived Scripts

This directory contains legacy scripts that have been replaced or are no longer used in the current pipeline.

## Archived Scripts by Category

### JQ Scripts (Replaced or Integrated)
- **add_testing_info_block.jq** - Replaced by add_info.jq in jq/
- **add_tests.jq** - Replaced by add_tests.js (JavaScript version)
- **create_env_payload.jq** - Functionality integrated into Makefile
- **create_mock_payload.jq** - Functionality integrated into Makefile
- **full_publish_payload.jq** - Not used in current pipeline
- **link_env_to_mock_payload.jq** - Functionality integrated into Makefile
- **link_payload.jq** - Functionality integrated into Makefile
- **postman_import_payload.jq** - Functionality integrated into Makefile
- **update_mock_env_payload.jq** - Functionality integrated into Makefile
- **update_mock_payload.jq** - Functionality integrated into Makefile
- **update_payload.jq** - Not used
- **url_hardfix_with_paths.jq** - Experimental, not used
- **verify_mock.jq** - Not used

### Python Scripts (Legacy Versions)
- **ebnf_to_openapi_class_based.py** - Earlier version, replaced by ebnf_to_openapi_dynamic_v3.py
- **analyze_endpoint_elements_v2.py** - Analysis script for development
- **extract_endpoint_ebnf_ordered.py** - Analysis script for development

### Shell/JS Scripts (Replaced by Makefile)
- **generate-postman.sh** - Functionality now in Makefile targets
- **quick-validate.sh** - Replaced by Makefile validation targets
- **inject-banner-correctly.js** - Banner injection, unclear if still needed
- **merge-postman.js** - Collection merging, may be useful for complex merges

## Archive Date
August 30, 2025

## Note
These scripts are kept for historical reference and potential future use. They should not be used in the current pipeline without careful review and testing.
EOF
    print_color $GREEN "  ✓ Created README.md in archived/"
}

# Help message
show_help() {
    cat << EOF
Archive Legacy Scripts Tool

Usage: $0 [option]

Options:
    --dry-run    Preview what would be archived (default)
    --execute    Perform the actual archiving
    --help       Show this help message

This script archives legacy and unused scripts to the archived/ directory
and moves misplaced scripts to their correct locations.
EOF
}

# Main execution
case "$MODE" in
    --dry-run)
        dry_run
        ;;
    --execute)
        print_color $RED "WARNING: This will move scripts to the archived directory!"
        read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            execute
        else
            print_color $YELLOW "Archiving cancelled"
        fi
        ;;
    --help|*)
        show_help
        ;;
esac