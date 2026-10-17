#!/bin/bash
# Fix all broken symlinks and replace with actual files

echo "🔧 Fixing all symlinks..."

# Function to copy file if source exists
copy_if_exists() {
    local source=$1
    local dest=$2
    
    if [ -f "$source" ]; then
        cp "$source" "$dest"
        echo "✅ Fixed: $dest"
    else
        echo "❌ Source not found: $source"
    fi
}

# Fix each README symlink
copy_if_exists "user-guides/development/postman-README.md" "./postman/README.md"
copy_if_exists "user-guides/development/openapi-README.md" "./openapi/README.md"
copy_if_exists "user-guides/development/data_dictionary-README.md" "./data_dictionary/README.md"
copy_if_exists "user-guides/development/tests-README.md" "./tests/README.md"
copy_if_exists "user-guides/archive/sdk-README.md" "./sdk/README.md"
copy_if_exists "user-guides/archive/sdk-clients-README.md" "./sdk-clients/README.md"
copy_if_exists "user-guides/archive/sdk-clients-python-README.md" "./sdk-clients/python/README.md"
copy_if_exists "user-guides/archive/sdk-clients-javascript-README.md" "./sdk-clients/javascript/README.md"
copy_if_exists "user-guides/development/examples-README.md" "./examples/README.md"
copy_if_exists "user-guides/development/scripts-README.md" "./scripts/README.md"
copy_if_exists "user-guides/development/scripts-archived-README.md" "./scripts/archived/README.md"
copy_if_exists "user-guides/development/github-README.md" "./.github/README.md"
copy_if_exists "user-guides/development/github-workflows-README.md" "./.github/workflows/README.md"

# Handle finspect files that don't exist - create placeholder
mkdir -p finspect
echo "# Finspect

Financial document inspection utilities.

See main documentation for details." > finspect/README.md

echo "# File Type Detection Methods

Documentation for file type detection methods used in finspect.

See main documentation for details." > finspect/file-type-detection-methods.md

echo "✅ Finspect placeholder files created"

# Also fix SDK READMEs that might be referenced
copy_if_exists "user-guides/archive/sdk-python-README.md" "./sdk/python/README.md"
copy_if_exists "user-guides/archive/sdk-javascript-README.md" "./sdk/javascript/README.md"

echo "✅ All symlinks replaced with actual files"