#!/bin/bash
# Fix all broken symlinks and replace with actual files

echo "🔧 Fixing all symlinks..."

# Define mappings for moved files
declare -A file_mappings=(
    ["postman-README.md"]="development/postman-README.md"
    ["openapi-README.md"]="development/openapi-README.md"
    ["data_dictionary-README.md"]="development/data_dictionary-README.md"
    ["tests-README.md"]="development/tests-README.md"
    ["sdk-README.md"]="archive/sdk-README.md"
    ["sdk-clients-README.md"]="archive/sdk-clients-README.md"
    ["sdk-clients-python-README.md"]="archive/sdk-clients-python-README.md"
    ["sdk-clients-javascript-README.md"]="archive/sdk-clients-javascript-README.md"
    ["examples-README.md"]="development/examples-README.md"
    ["scripts-README.md"]="development/scripts-README.md"
    ["scripts-archived-README.md"]="archive/scripts-archived-README.md"
    ["github-README.md"]="development/github-README.md"
    ["github-workflows-README.md"]="development/github-workflows-README.md"
)

# Remove and recreate symlinks with correct paths
fix_symlink() {
    local symlink_path=$1
    local target_file=$2
    local new_target_dir=$3
    
    echo "Fixing: $symlink_path"
    rm -f "$symlink_path"
    
    # Calculate relative path from symlink to new target
    local symlink_dir=$(dirname "$symlink_path")
    local relative_path=$(python3 -c "import os.path; print(os.path.relpath('user-guides/$new_target_dir/$target_file', '$symlink_dir'))")
    
    # Create actual file copy instead of symlink for GitHub
    cp "user-guides/$new_target_dir/$target_file" "$symlink_path"
}

# Fix each symlink
fix_symlink "./postman/README.md" "postman-README.md" "development"
fix_symlink "./openapi/README.md" "openapi-README.md" "development"
fix_symlink "./data_dictionary/README.md" "data_dictionary-README.md" "development"
fix_symlink "./tests/README.md" "tests-README.md" "development"
fix_symlink "./sdk/README.md" "sdk-README.md" "archive"
fix_symlink "./sdk-clients/README.md" "sdk-clients-README.md" "archive"
fix_symlink "./sdk-clients/python/README.md" "sdk-clients-python-README.md" "archive"
fix_symlink "./sdk-clients/javascript/README.md" "sdk-clients-javascript-README.md" "archive"
fix_symlink "./examples/README.md" "examples-README.md" "development"
fix_symlink "./scripts/README.md" "scripts-README.md" "development"
fix_symlink "./scripts/archived/README.md" "scripts-archived-README.md" "archive"
fix_symlink "./.github/README.md" "github-README.md" "development"
fix_symlink "./.github/workflows/README.md" "github-workflows-README.md" "development"

# Handle finspect files that don't exist - create placeholder
mkdir -p finspect
echo "# Finspect

Financial document inspection utilities.

See main documentation for details." > finspect/README.md

echo "# File Type Detection Methods

Documentation for file type detection methods used in finspect.

See main documentation for details." > finspect/file-type-detection-methods.md

echo "✅ All symlinks fixed and replaced with actual files"