#!/bin/bash

# Move potentially deletable files to possible-trash folder
# This script organizes files by category for easy review before deletion

# Set project root
PROJECT_ROOT="/Users/frankserrao/Dropbox/Customers/c2m/projects/c2m-api/C2M_API_v3/c2m-api-repo"
TRASH_DIR="$PROJECT_ROOT/possible-trash"

# Create main trash directory
mkdir -p "$TRASH_DIR"

# Create category subdirectories
mkdir -p "$TRASH_DIR/macos-system-files"
mkdir -p "$TRASH_DIR/python-cache"
mkdir -p "$TRASH_DIR/log-files"
mkdir -p "$TRASH_DIR/pid-files"
mkdir -p "$TRASH_DIR/debug-files"
mkdir -p "$TRASH_DIR/generated-reports"
mkdir -p "$TRASH_DIR/temp-and-backup"
mkdir -p "$TRASH_DIR/unusual-names"
mkdir -p "$TRASH_DIR/test-media"
mkdir -p "$TRASH_DIR/package-info"

# Change to project root
cd "$PROJECT_ROOT"

echo "🗑️  Moving potentially deletable files to possible-trash..."
echo "================================================"

# 1. Move .DS_Store files
echo "📁 Moving .DS_Store files..."
find . -path "./possible-trash" -prune -o -path "./node_modules" -prune -o -path "./.git" -prune -o -name ".DS_Store" -type f -print0 | while IFS= read -r -d '' file; do
    # Create directory structure in trash
    dir=$(dirname "$file")
    mkdir -p "$TRASH_DIR/macos-system-files/$dir"
    mv "$file" "$TRASH_DIR/macos-system-files/$file" 2>/dev/null && echo "  Moved: $file"
done

# 2. Move Python cache files
echo "🐍 Moving Python cache files..."
# Move .pyc files
find . -path "./possible-trash" -prune -o -path "./node_modules" -prune -o -path "./.git" -prune -o -path "./scripts/python_env" -prune -o -name "*.pyc" -type f -print0 | while IFS= read -r -d '' file; do
    dir=$(dirname "$file")
    mkdir -p "$TRASH_DIR/python-cache/$dir"
    mv "$file" "$TRASH_DIR/python-cache/$file" 2>/dev/null && echo "  Moved: $file"
done

# Move __pycache__ directories
find . -path "./possible-trash" -prune -o -path "./node_modules" -prune -o -path "./.git" -prune -o -path "./scripts/python_env" -prune -o -name "__pycache__" -type d -print0 | while IFS= read -r -d '' dir; do
    parent=$(dirname "$dir")
    mkdir -p "$TRASH_DIR/python-cache/$parent"
    mv "$dir" "$TRASH_DIR/python-cache/$dir" 2>/dev/null && echo "  Moved: $dir/"
done

# 3. Move log files
echo "📝 Moving log files..."
[ -f "postman/prism.log" ] && mv "postman/prism.log" "$TRASH_DIR/log-files/" && echo "  Moved: postman/prism.log"
[ -f "DocumentationAndNotes/c2m_todo/General/BeingWrittenToBaseDir/prism.log" ] && {
    mkdir -p "$TRASH_DIR/log-files/DocumentationAndNotes/c2m_todo/General/BeingWrittenToBaseDir"
    mv "DocumentationAndNotes/c2m_todo/General/BeingWrittenToBaseDir/prism.log" "$TRASH_DIR/log-files/DocumentationAndNotes/c2m_todo/General/BeingWrittenToBaseDir/" && echo "  Moved: DocumentationAndNotes/.../prism.log"
}

# 4. Move PID files
echo "🔢 Moving PID files..."
[ -f "postman/prism_pid.txt" ] && mv "postman/prism_pid.txt" "$TRASH_DIR/pid-files/" && echo "  Moved: postman/prism_pid.txt"
[ -f "docs/http_pid.txt" ] && mv "docs/http_pid.txt" "$TRASH_DIR/pid-files/" && echo "  Moved: docs/http_pid.txt"
[ -f "Old/docs.bak/http_pid.txt" ] && {
    mkdir -p "$TRASH_DIR/pid-files/Old/docs.bak"
    mv "Old/docs.bak/http_pid.txt" "$TRASH_DIR/pid-files/Old/docs.bak/" && echo "  Moved: Old/docs.bak/http_pid.txt"
}

# 5. Move debug files
echo "🐛 Moving debug files..."
for file in postman/*-debug.json; do
    if [ -f "$file" ]; then
        mv "$file" "$TRASH_DIR/debug-files/" && echo "  Moved: $file"
    fi
done

# 6. Move generated reports
echo "📊 Moving generated reports..."
[ -f "postman/newman-report.html" ] && mv "postman/newman-report.html" "$TRASH_DIR/generated-reports/" && echo "  Moved: postman/newman-report.html"
[ -f "postman/prism-mock-test-report.html" ] && mv "postman/prism-mock-test-report.html" "$TRASH_DIR/generated-reports/" && echo "  Moved: postman/prism-mock-test-report.html"

# Move finspect reports
for file in finspect/frank-tests/finspect_report_*; do
    if [ -f "$file" ]; then
        mkdir -p "$TRASH_DIR/generated-reports/finspect/frank-tests"
        mv "$file" "$TRASH_DIR/generated-reports/finspect/frank-tests/" && echo "  Moved: $file"
    fi
done

# 7. Move temp and backup files
echo "💾 Moving temp and backup files..."
[ -f "docs/template-editor.png.new" ] && mv "docs/template-editor.png.new" "$TRASH_DIR/temp-and-backup/" && echo "  Moved: docs/template-editor.png.new"
[ -f "postman/custom/overrides.json.old" ] && {
    mkdir -p "$TRASH_DIR/temp-and-backup/postman/custom"
    mv "postman/custom/overrides.json.old" "$TRASH_DIR/temp-and-backup/postman/custom/" && echo "  Moved: postman/custom/overrides.json.old"
}

# 8. Move files with unusual names
echo "🤔 Moving files with unusual names..."
[ -f "data_dictionary/Awesome—here's a clean, implementation-r.yml" ] && mv "data_dictionary/Awesome—here's a clean, implementation-r.yml" "$TRASH_DIR/unusual-names/" && echo "  Moved: Awesome—here's..."
[ -f "data_dictionary/Option A — Import the OpenAPI with folderStrategy_ none (true flatten at source) (1).pdf" ] && mv "data_dictionary/Option A — Import the OpenAPI with folderStrategy_ none (true flatten at source) (1).pdf" "$TRASH_DIR/unusual-names/" && echo "  Moved: Option A — Import..."
[ -f "data_dictionary/⏺ SummaryOfClaudeCodeChangesForJWT.yml" ] && mv "data_dictionary/⏺ SummaryOfClaudeCodeChangesForJWT.yml" "$TRASH_DIR/unusual-names/" && echo "  Moved: ⏺ SummaryOfClaudeCodeChangesForJWT.yml"

# 9. Move package info (optional - commented out by default)
echo "📦 Package info (skipping - uncomment to move)..."
# [ -d "finspect/finspect.egg-info" ] && mv "finspect/finspect.egg-info" "$TRASH_DIR/package-info/" && echo "  Moved: finspect/finspect.egg-info/"

# 10. Move test media files (optional - commented out by default as they might be needed)
echo "🎬 Test media files (skipping - uncomment to move)..."
# if [ -d "finspect/frank-tests" ]; then
#     mkdir -p "$TRASH_DIR/test-media/finspect"
#     for ext in mkv mov HEIC png gif webp pdf epub docx rar; do
#         for file in finspect/frank-tests/*.$ext; do
#             [ -f "$file" ] && mv "$file" "$TRASH_DIR/test-media/finspect/frank-tests/" && echo "  Moved: $file"
#         done
#     done
# fi

echo ""
echo "✅ Move complete!"
echo ""
echo "📊 Summary:"
echo "- All potentially deletable files have been moved to: $TRASH_DIR"
echo "- Files are organized by category for easy review"
echo "- Test media files and package info were NOT moved (uncomment in script if needed)"
echo ""
echo "🔍 Next steps:"
echo "1. Review the contents of possible-trash/"
echo "2. Delete the entire folder when confirmed: rm -rf possible-trash/"
echo "3. Add patterns to .gitignore to prevent these files from returning"