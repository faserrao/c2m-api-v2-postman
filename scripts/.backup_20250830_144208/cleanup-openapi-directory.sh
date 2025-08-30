#!/bin/bash

# Cleanup script for the openapi directory
# This script moves backup and outdated OpenAPI spec files to possible-trash

# Set project root
PROJECT_ROOT="/Users/frankserrao/Dropbox/Customers/c2m/projects/c2m-api/C2M_API_v3/c2m-api-repo"
TRASH_DIR="$PROJECT_ROOT/possible-trash"
OPENAPI_TRASH="$TRASH_DIR/openapi-cleanup"

# Create trash directories
mkdir -p "$OPENAPI_TRASH/backups"
mkdir cryptv
mkdir -p "$OPENAPI_TRASH/old-examples"

# Change to openapi directory
cd "$PROJECT_ROOT/openapi"

echo "🧹 Cleaning up openapi directory..."
echo "================================================"

# 1. Move timestamped backup files
echo "💾 Moving backup files..."
for file in *.yaml.*[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]; do
    if [ -f "$file" ]; then
        mv "$file" "$OPENAPI_TRASH/backups/" && echo "  ✓ Moved: $file"
    fi
done

# 2. Check example files
echo "📝 Checking example files..."
# The -with-examples.yaml file is used by PRISM_SPEC in Makefile, so we keep it
echo "  ℹ️  Keeping: c2mapiv2-openapi-spec-final-with-examples.yaml (used by PRISM_SPEC)"

# 3. Check for any other potential cleanup files
echo "🔍 Checking for other cleanup candidates..."

# Look for files with common backup patterns
for pattern in "*~" "*.bak" "*.old" "*.backup" "*copy*" "*test*" "*temp*" "*draft*"; do
    for file in $pattern; do
        if [ -f "$file" ] && [ "$file" != "$pattern" ]; then
            case "$file" in
                # Don't move essential files even if they match patterns
                "c2mapiv2-openapi-spec-final.yaml" | \
                "c2mapiv2-openapi-spec-base.yaml" | \
                "bundled.yaml")
                    echo "  ⏭️  Keeping: $file (essential file)"
                    ;;
                *)
                    mv "$file" "$OPENAPI_TRASH/backups/" && echo "  ✓ Moved: $file"
                    ;;
            esac
        fi
    done
done

# 4. Check Old directory if it still exists (might not have been moved yet)
if [ -d "Old" ]; then
    echo "📁 Found Old directory..."
    mv "Old" "$OPENAPI_TRASH/" && echo "  ✓ Moved: Old/ directory"
fi

# 5. List what's kept
echo ""
echo "✅ OpenAPI directory cleanup complete!"
echo ""
echo "📊 Essential files kept:"
echo "- c2mapiv2-openapi-spec-final.yaml (main spec)"
echo "- c2mapiv2-openapi-spec-base.yaml (base spec)"
echo "- bundled.yaml (bundled/merged spec)"
echo "- overlays/ directory (auth overlays)"
echo ""

# Check if examples directory exists
if [ -d "examples" ]; then
    echo "📂 Also kept: examples/ directory"
fi

echo "🔍 Moved files are in: $OPENAPI_TRASH"
echo ""

# Show sizes
if [ -d "$OPENAPI_TRASH" ]; then
    echo "💾 Space saved:"
    du -sh "$OPENAPI_TRASH"
fi

echo ""
echo "💡 Tip: The *-with-examples.yaml file can be regenerated using:"
echo "   make postman-openapi-spec-add-examples"