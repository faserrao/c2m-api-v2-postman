#!/bin/bash

# Cleanup script specifically for the scripts directory
# This script moves potentially obsolete scripts to possible-trash

# Set project root (two levels up from scripts/utilities/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TRASH_DIR="$PROJECT_ROOT/possible-trash"
SCRIPTS_TRASH="$TRASH_DIR/scripts-cleanup"

# Create trash directories
mkdir -p "$SCRIPTS_TRASH/old-versions"
mkdir -p "$SCRIPTS_TRASH/duplicate-banner-scripts"
mkdir -p "$SCRIPTS_TRASH/test-data"
mkdir -p "$SCRIPTS_TRASH/one-time-scripts"
mkdir -p "$SCRIPTS_TRASH/duplicate-jq"
mkdir -p "$SCRIPTS_TRASH/superseded"
mkdir -p "$SCRIPTS_TRASH/experimental"
mkdir -p "$SCRIPTS_TRASH/temp-and-backup"

# Change to scripts directory
cd "$PROJECT_ROOT/scripts"

echo "🧹 Cleaning up scripts directory..."
echo "================================================"

# 1. Move old versions of EBNF converters
echo "📦 Moving old EBNF converter versions..."
[ -f "ebnf_to_openapi_dynamic_v3_backup.py" ] && mv "ebnf_to_openapi_dynamic_v3_backup.py" "$SCRIPTS_TRASH/old-versions/" && echo "  ✓ Moved: ebnf_to_openapi_dynamic_v3_backup.py"
[ -f "ebnf_to_openapi_dynamic_v2.py" ] && mv "ebnf_to_openapi_dynamic_v2.py" "$SCRIPTS_TRASH/old-versions/" && echo "  ✓ Moved: ebnf_to_openapi_dynamic_v2.py"
[ -f "ebnf_to_openapi_dynamic.py" ] && mv "ebnf_to_openapi_dynamic.py" "$SCRIPTS_TRASH/old-versions/" && echo "  ✓ Moved: ebnf_to_openapi_dynamic.py"

# 2. Move superseded scripts
echo "🔄 Moving superseded scripts..."
[ -f "analyze_endpoint_elements.py" ] && mv "analyze_endpoint_elements.py" "$SCRIPTS_TRASH/superseded/" && echo "  ✓ Moved: analyze_endpoint_elements.py"
[ -f "fix_collection_urls.py" ] && mv "fix_collection_urls.py" "$SCRIPTS_TRASH/superseded/" && echo "  ✓ Moved: fix_collection_urls.py"
[ -f "extract_endpoint_ebnf.py" ] && mv "extract_endpoint_ebnf.py" "$SCRIPTS_TRASH/superseded/" && echo "  ✓ Moved: extract_endpoint_ebnf.py"

# 3. Move duplicate banner scripts (keeping inject-banner-correctly.js and fix-template-banner.sh)
echo "🎨 Moving duplicate banner scripts..."
[ -f "inject-banner.js" ] && mv "inject-banner.js" "$SCRIPTS_TRASH/duplicate-banner-scripts/" && echo "  ✓ Moved: inject-banner.js"
[ -f "inject-banner-simple.js" ] && mv "inject-banner-simple.js" "$SCRIPTS_TRASH/duplicate-banner-scripts/" && echo "  ✓ Moved: inject-banner-simple.js"
[ -f "add-banner-to-spec.js" ] && mv "add-banner-to-spec.js" "$SCRIPTS_TRASH/duplicate-banner-scripts/" && echo "  ✓ Moved: add-banner-to-spec.js"
echo "  ℹ️  Keeping: inject-banner-correctly.js (appears to be the current version)"
echo "  ℹ️  Keeping: fix-template-banner.sh (referenced in Makefile)"

# 4. Move test data files
echo "🧪 Moving test data files..."
if [ -d "test_data_generator_for_collections" ]; then
    [ -f "test_data_generator_for_collections/test-collection.json" ] && \
        mv "test_data_generator_for_collections/test-collection.json" "$SCRIPTS_TRASH/test-data/" && \
        echo "  ✓ Moved: test_data_generator_for_collections/test-collection.json"
    [ -f "test_data_generator_for_collections/test-collection-randomized.json" ] && \
        mv "test_data_generator_for_collections/test-collection-randomized.json" "$SCRIPTS_TRASH/test-data/" && \
        echo "  ✓ Moved: test_data_generator_for_collections/test-collection-randomized.json"
fi

if [ -d "test_data_generator_for_openapi_specs" ]; then
    cd test_data_generator_for_openapi_specs
    for file in testing-generator.json test_example.py c2m-api-public.yml c2m.collection.merged*.json c2m_openapi_spec_final.yaml claude-code-spec_generating-openapi-with-examples.md; do
        if [ -f "$file" ]; then
            mv "$file" "$SCRIPTS_TRASH/test-data/" && echo "  ✓ Moved: test_data_generator_for_openapi_specs/$file"
        fi
    done
    cd ..
fi

# 5. Move one-time makefile scripts
echo "🔧 Moving one-time makefile scripts..."
if [ -d "makefile-scripts" ]; then
    cd makefile-scripts
    for script in make-force-rebuild-change.sh undo-make-force-rebuild-change.sh add-force-rebuild.sh mod-force-rebuild.sh backup-makefile.sh; do
        [ -f "$script" ] && mv "$script" "$SCRIPTS_TRASH/one-time-scripts/" && echo "  ✓ Moved: makefile-scripts/$script"
    done
    
    # Move duplicate orchestrator scripts (keep v2)
    [ -f "fix-orchestrator.sh" ] && mv "fix-orchestrator.sh" "$SCRIPTS_TRASH/old-versions/" && echo "  ✓ Moved: fix-orchestrator.sh"
    [ -f "fix-orchestrator_v2.sh" ] && mv "fix-orchestrator_v2.sh" "$SCRIPTS_TRASH/old-versions/" && echo "  ✓ Moved: fix-orchestrator_v2.sh (duplicate)"
    echo "  ℹ️  Keeping: fix-orchestrator-v2.sh (current version)"
    
    # Move patch files
    [ -f "refactor-orchestrator.patch" ] && mv "refactor-orchestrator.patch" "$SCRIPTS_TRASH/one-time-scripts/" && echo "  ✓ Moved: refactor-orchestrator.patch"
    cd ..
fi

# 6. Move duplicate JQ scripts (keep versions in jq/ subdirectory)
echo "📜 Moving duplicate JQ scripts..."
[ -f "sanitize_collection.jq" ] && mv "sanitize_collection.jq" "$SCRIPTS_TRASH/duplicate-jq/" && echo "  ✓ Moved: sanitize_collection.jq (duplicate)"
[ -f "fix_urls.jq" ] && mv "fix_urls.jq" "$SCRIPTS_TRASH/duplicate-jq/" && echo "  ✓ Moved: fix_urls.jq (duplicate)"
[ -f "auto_fix_collection.jq" ] && mv "auto_fix_collection.jq" "$SCRIPTS_TRASH/duplicate-jq/" && echo "  ✓ Moved: auto_fix_collection.jq (duplicate)"
[ -f "verify_urls.jq" ] && mv "verify_urls.jq" "$SCRIPTS_TRASH/duplicate-jq/" && echo "  ✓ Moved: verify_urls.jq (duplicate)"

# 7. Move experimental scripts
echo "🔬 Moving experimental scripts..."
[ -f "ebnf_to_openapi_grammer_based.py" ] && mv "ebnf_to_openapi_grammer_based.py" "$SCRIPTS_TRASH/experimental/" && echo "  ✓ Moved: ebnf_to_openapi_grammer_based.py"
[ -f "replace-enum-values.js" ] && mv "replace-enum-values.js" "$SCRIPTS_TRASH/experimental/" && echo "  ✓ Moved: replace-enum-values.js"

# 8. Move possibly redundant URL scripts
echo "🔗 Moving possibly redundant URL scripts..."
[ -f "url_hardfix.jq" ] && mv "url_hardfix.jq" "$SCRIPTS_TRASH/superseded/" && echo "  ✓ Moved: url_hardfix.jq"
[ -f "repair_urls.py" ] && mv "repair_urls.py" "$SCRIPTS_TRASH/superseded/" && echo "  ✓ Moved: repair_urls.py"

# 9. Move temp and backup files
echo "💾 Moving temp and backup files..."
[ -f "env_template (Unicode Encoding Conflict).jq" ] && mv "env_template (Unicode Encoding Conflict).jq" "$SCRIPTS_TRASH/temp-and-backup/" && echo "  ✓ Moved: env_template (Unicode Encoding Conflict).jq"

# 10. Move init scripts (one-time use)
echo "🚀 Moving initialization scripts..."
[ -f "init-directory-structure.sh" ] && mv "init-directory-structure.sh" "$SCRIPTS_TRASH/one-time-scripts/" && echo "  ✓ Moved: init-directory-structure.sh"

# 11. Move the cleanup scripts themselves (after use)
echo "🧹 Moving cleanup scripts (meta!)..."
[ -f "move-to-possible-trash.sh" ] && mv "move-to-possible-trash.sh" "$SCRIPTS_TRASH/one-time-scripts/" && echo "  ✓ Moved: move-to-possible-trash.sh"
[ -f "move-to-possible-trash-extended.sh" ] && mv "move-to-possible-trash-extended.sh" "$SCRIPTS_TRASH/one-time-scripts/" && echo "  ✓ Moved: move-to-possible-trash-extended.sh"

echo ""
echo "✅ Scripts directory cleanup complete!"
echo ""
echo "📊 Summary of what was kept:"
echo "- ebnf_to_openapi_class_based.py (current EBNF converter)"
echo "- ebnf_to_openapi_dynamic_v3.py (latest dynamic version)"
echo "- inject-banner-correctly.js (current banner script)"
echo "- fix-orchestrator-v2.sh (current orchestrator fix)"
echo "- All scripts in jq/ subdirectory"
echo "- Core utilities (validate_collection.js, generate_test_data.py, etc.)"
echo "- Active scripts referenced in Makefile"
echo ""
echo "🔍 Moved files are in: $SCRIPTS_TRASH"
echo ""
echo "⚠️  Important: Review the Makefile to ensure no moved scripts are still referenced!"
echo "   grep -E '(inject-banner|fix_collection_urls|ebnf_to_openapi_dynamic)' ../Makefile"