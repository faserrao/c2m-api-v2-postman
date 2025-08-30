#!/bin/bash

# Extended cleanup script - Move additional potentially deletable files to possible-trash folder
# This script handles more file types and entire directories that appear to be outdated

# Set project root
PROJECT_ROOT="/Users/frankserrao/Dropbox/Customers/c2m/projects/c2m-api/C2M_API_v3/c2m-api-repo"
TRASH_DIR="$PROJECT_ROOT/possible-trash"

# Create main trash directory if it doesn't exist
mkdir -p "$TRASH_DIR"

# Create extended category subdirectories
mkdir -p "$TRASH_DIR/old-directories"
mkdir -p "$TRASH_DIR/backup-files"
mkdir -p "$TRASH_DIR/debug-json"
mkdir -p "$TRASH_DIR/build-artifacts"
mkdir -p "$TRASH_DIR/test-specs"
mkdir -p "$TRASH_DIR/documentation-pdfs"
mkdir -p "$TRASH_DIR/copy-files"
mkdir -p "$TRASH_DIR/tracking-files"

# Change to project root
cd "$PROJECT_ROOT"

echo "🗑️  Extended cleanup - Moving additional files to possible-trash..."
echo "================================================"

# 1. Move entire Old directories
echo "📁 Moving old directories..."
if [ -d "Old" ]; then
    echo "  Moving Old/ directory..."
    mv "Old" "$TRASH_DIR/old-directories/" 2>/dev/null && echo "  ✓ Moved: Old/"
fi

if [ -d "postman/generated/Old" ]; then
    mkdir -p "$TRASH_DIR/old-directories/postman/generated"
    mv "postman/generated/Old" "$TRASH_DIR/old-directories/postman/generated/" 2>/dev/null && echo "  ✓ Moved: postman/generated/Old/"
fi

if [ -d "openapi/Old" ]; then
    mkdir -p "$TRASH_DIR/old-directories/openapi"
    mv "openapi/Old" "$TRASH_DIR/old-directories/openapi/" 2>/dev/null && echo "  ✓ Moved: openapi/Old/"
fi

if [ -d "DocumentationAndNotes/c2m_todo/ScriptsStuff/Old" ]; then
    mkdir -p "$TRASH_DIR/old-directories/DocumentationAndNotes/c2m_todo/ScriptsStuff"
    mv "DocumentationAndNotes/c2m_todo/ScriptsStuff/Old" "$TRASH_DIR/old-directories/DocumentationAndNotes/c2m_todo/ScriptsStuff/" 2>/dev/null && echo "  ✓ Moved: DocumentationAndNotes/.../Old/"
fi

# 2. Move backup files (.bak, .old)
echo "💾 Moving backup files..."
find . -path "./possible-trash" -prune -o -path "./node_modules" -prune -o -path "./.git" -prune -o \
    \( -name "*.bak" -o -name "*.old" -o -name "*~" \) -type f -print0 | while IFS= read -r -d '' file; do
    dir=$(dirname "$file")
    mkdir -p "$TRASH_DIR/backup-files/$dir"
    mv "$file" "$TRASH_DIR/backup-files/$file" 2>/dev/null && echo "  ✓ Moved: $file"
done

# 3. Move debug JSON files
echo "🐛 Moving debug JSON files..."
for file in postman/debug-*.json postman/monk_link_debug.json; do
    if [ -f "$file" ]; then
        mv "$file" "$TRASH_DIR/debug-json/" 2>/dev/null && echo "  ✓ Moved: $file"
    fi
done

# 4. Move gen directory (build artifacts)
echo "🏗️  Moving build artifacts..."
if [ -d "gen" ]; then
    mv "gen" "$TRASH_DIR/build-artifacts/" 2>/dev/null && echo "  ✓ Moved: gen/"
fi

# 5. Move test spec files
echo "🧪 Moving test spec files..."
if [ -d "scripts/test_data_generator_for_openapi_specs" ]; then
    for file in scripts/test_data_generator_for_openapi_specs/*.yaml; do
        if [ -f "$file" ] && [[ "$file" == *"-with-examples.yaml" || "$file" == *"test_spec"* ]]; then
            mkdir -p "$TRASH_DIR/test-specs/scripts/test_data_generator_for_openapi_specs"
            mv "$file" "$TRASH_DIR/test-specs/scripts/test_data_generator_for_openapi_specs/" 2>/dev/null && echo "  ✓ Moved: $file"
        fi
    done
fi

# 6. Move copy files
echo "📄 Moving copy files..."
find . -path "./possible-trash" -prune -o -path "./node_modules" -prune -o -path "./.git" -prune -o \
    -name "*copy*" -type f -print0 | while IFS= read -r -d '' file; do
    dir=$(dirname "$file")
    mkdir -p "$TRASH_DIR/copy-files/$dir"
    mv "$file" "$TRASH_DIR/copy-files/$file" 2>/dev/null && echo "  ✓ Moved: $file"
done

# 7. Move tracking text files from postman
echo "📝 Moving Postman tracking files..."
for file in postman/*.txt; do
    if [ -f "$file" ]; then
        # Skip important files
        case "$(basename "$file")" in
            postman_api_uid.txt|postman_ws_uid.txt|postman_mock_url.txt)
                echo "  ⏭️  Keeping: $file (active tracking file)"
                ;;
            *)
                mv "$file" "$TRASH_DIR/tracking-files/" 2>/dev/null && echo "  ✓ Moved: $file"
                ;;
        esac
    fi
done

# 8. Move documentation PDFs
echo "📚 Moving documentation PDFs..."
find DocumentationAndNotes -name "*.pdf" -type f | while IFS= read -r file; do
    # Check if it's a Google search result or copy
    if [[ "$file" == *"Google Search"* ]] || [[ "$file" == *"copy"* ]]; then
        dir=$(dirname "$file")
        mkdir -p "$TRASH_DIR/documentation-pdfs/$dir"
        mv "$file" "$TRASH_DIR/documentation-pdfs/$file" 2>/dev/null && echo "  ✓ Moved: $file"
    fi
done

# 9. Move translation report
echo "📊 Moving translation report..."
[ -f "openapi/translation-report.txt" ] && {
    mkdir -p "$TRASH_DIR/generated-reports/openapi"
    mv "openapi/translation-report.txt" "$TRASH_DIR/generated-reports/openapi/" 2>/dev/null && echo "  ✓ Moved: openapi/translation-report.txt"
}

# 10. Move test images directory
echo "🖼️  Moving test images..."
if [ -d "test-images" ]; then
    mv "test-images" "$TRASH_DIR/" 2>/dev/null && echo "  ✓ Moved: test-images/"
fi

# 11. Move additional PID files
echo "🔢 Moving additional PID files..."
[ -f "DocumentationAndNotes/c2m_todo/General/BeingWrittenToBaseDir/prism.pid" ] && {
    mkdir -p "$TRASH_DIR/pid-files/DocumentationAndNotes/c2m_todo/General/BeingWrittenToBaseDir"
    mv "DocumentationAndNotes/c2m_todo/General/BeingWrittenToBaseDir/prism.pid" "$TRASH_DIR/pid-files/DocumentationAndNotes/c2m_todo/General/BeingWrittenToBaseDir/" 2>/dev/null && echo "  ✓ Moved: .../prism.pid"
}

# 12. Check for any remaining .DS_Store files
echo "🍎 Checking for remaining .DS_Store files..."
find . -path "./possible-trash" -prune -o -path "./node_modules" -prune -o -path "./.git" -prune -o -name ".DS_Store" -type f -print0 | while IFS= read -r -d '' file; do
    dir=$(dirname "$file")
    mkdir -p "$TRASH_DIR/macos-system-files/$dir"
    mv "$file" "$TRASH_DIR/macos-system-files/$file" 2>/dev/null && echo "  ✓ Moved: $file"
done

echo ""
echo "✅ Extended cleanup complete!"
echo ""
echo "📊 Summary:"
echo "- All identified files have been moved to: $TRASH_DIR"
echo "- Files are organized by category for easy review"
echo "- Important tracking files were preserved"
echo ""
echo "🔍 Next steps:"
echo "1. Review the contents of possible-trash/"
echo "2. Run 'du -sh possible-trash/*' to see space usage by category"
echo "3. Delete the entire folder when confirmed: rm -rf possible-trash/"
echo "4. Consider adding patterns to .gitignore to prevent these files from returning"
echo ""
echo "⚠️  Note: Some directories like 'Old/' contained significant amounts of data."
echo "Make sure to review before permanent deletion!"