#!/bin/bash

# Cleanup script for the docs directory
# This script moves screenshots, logs, and temporary files to possible-trash

# Set project root (two levels up from scripts/utilities/)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TRASH_DIR="$PROJECT_ROOT/possible-trash"
DOCS_TRASH="$TRASH_DIR/docs-cleanup"

# Create trash directories
mkdir -p "$DOCS_TRASH/screenshots"
mkdir -p "$DOCS_TRASH/logs"
mkdir -p "$DOCS_TRASH/previous-versions"
mkdir -p "$DOCS_TRASH/temp-files"
mkdir -p "$DOCS_TRASH/generated"

# Change to docs directory
cd "$PROJECT_ROOT/docs"

echo "🧹 Cleaning up docs directory..."
echo "================================================"

# 1. Move screenshots
echo "📸 Moving screenshots..."
for file in "Screenshot "*.png; do
    if [ -f "$file" ]; then
        mv "$file" "$DOCS_TRASH/screenshots/" && echo "  ✓ Moved: $file"
    fi
done

# Move other image files that appear to be temporary
[ -f "previous-docs-look.png" ] && mv "previous-docs-look.png" "$DOCS_TRASH/previous-versions/" && echo "  ✓ Moved: previous-docs-look.png"
[ -f "template-editor.png" ] && mv "template-editor.png" "$DOCS_TRASH/temp-files/" && echo "  ✓ Moved: template-editor.png"

# 2. Move log files
echo "📝 Moving log files..."
for logfile in log.*.txt; do
    if [ -f "$logfile" ]; then
        mv "$logfile" "$DOCS_TRASH/logs/" && echo "  ✓ Moved: $logfile"
    fi
done

# 3. Check for PID files (already handled in main cleanup, but check again)
echo "🔢 Checking for PID files..."
if [ -f "http_pid.txt" ]; then
    echo "  ⚠️  Found http_pid.txt - should have been moved already"
    mkdir -p "$DOCS_TRASH/pid-files"
    mv "http_pid.txt" "$DOCS_TRASH/pid-files/" && echo "  ✓ Moved: http_pid.txt"
fi

# 4. Move test documentation if not needed
echo "🧪 Checking test documentation..."
if [ -f "apiTestingReadme.md" ]; then
    # Check if it's referenced anywhere
    if ! grep -q "apiTestingReadme" ../Makefile && ! grep -q "apiTestingReadme" ../README.md; then
        mv "apiTestingReadme.md" "$DOCS_TRASH/temp-files/" && echo "  ✓ Moved: apiTestingReadme.md"
    else
        echo "  ℹ️  Keeping: apiTestingReadme.md (may be referenced)"
    fi
fi

# 5. Check generated files
echo "🏗️  Checking generated files..."
# Check if swagger.yaml is a duplicate
if [ -f "swagger.yaml" ]; then
    if diff -q "swagger.yaml" "../openapi/c2mapiv2-openapi-spec-final.yaml" >/dev/null 2>&1; then
        mv "swagger.yaml" "$DOCS_TRASH/generated/" && echo "  ✓ Moved: swagger.yaml (duplicate of main spec)"
    else
        echo "  ℹ️  Keeping: swagger.yaml (unique content)"
    fi
fi

# Keep redoc.html and swagger.html as they might have custom configurations
echo "  ℹ️  Keeping: redoc.html and swagger.html (may have custom configs)"

# 6. Check for backup or old files
echo "💾 Checking for backup files..."
for pattern in "*.bak" "*.old" "*.backup" "*~" "*copy*"; do
    for file in $pattern; do
        if [ -f "$file" ] && [ "$file" != "$pattern" ]; then
            mv "$file" "$DOCS_TRASH/temp-files/" && echo "  ✓ Moved: $file"
        fi
    done
done

# 7. Check for .DS_Store
echo "🍎 Checking for system files..."
if [ -f ".DS_Store" ]; then
    mkdir -p "$DOCS_TRASH/system-files"
    mv ".DS_Store" "$DOCS_TRASH/system-files/" && echo "  ✓ Moved: .DS_Store"
fi

echo ""
echo "✅ Docs directory cleanup complete!"
echo ""
echo "📊 Essential files kept:"
echo "- index.html, index.css, index.js (main documentation)"
echo "- All swagger-ui-* files (UI framework)"
echo "- Templates (*.hbs, *.template files)"
echo "- api.md and README.md"
echo "- Favicon files"
echo "- LICENSE and NOTICE"
echo "- package.json and utilities"
echo ""

# Show what was moved
echo "🔍 Moved files are in: $DOCS_TRASH"
echo ""

# Show sizes
if [ -d "$DOCS_TRASH" ]; then
    echo "💾 Space saved:"
    du -sh "$DOCS_TRASH"
    echo ""
    echo "📂 Breakdown by category:"
    du -sh "$DOCS_TRASH"/* 2>/dev/null | sort -rh
fi

echo ""
echo "💡 Tips:"
echo "- redoc.html can be regenerated with: make docs-build"
echo "- swagger.html can be regenerated from the OpenAPI spec"
echo "- Screenshots can be retaken if needed for documentation"