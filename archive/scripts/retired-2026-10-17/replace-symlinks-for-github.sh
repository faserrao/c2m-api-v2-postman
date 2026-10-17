#!/bin/bash
# Replace symlinks with actual files for GitHub Pages compatibility

echo "🔄 Replacing symlinks with actual files for GitHub..."

# Find all symlinks in the repo
find . -type l -name "*.md" | while read -r symlink; do
    # Skip node_modules
    if [[ $symlink == *"node_modules"* ]]; then
        continue
    fi
    
    # Get the target of the symlink
    target=$(readlink "$symlink")
    
    # Get the absolute path of the target
    if [[ $target == /* ]]; then
        # Absolute path
        target_path="$target"
    else
        # Relative path
        symlink_dir=$(dirname "$symlink")
        target_path="$symlink_dir/$target"
    fi
    
    # Normalize the path
    target_path=$(cd "$(dirname "$target_path")" 2>/dev/null && pwd)/$(basename "$target_path")
    
    # Check if target exists
    if [ -f "$target_path" ]; then
        echo "📋 Replacing symlink: $symlink -> $target"
        rm "$symlink"
        cp "$target_path" "$symlink"
    else
        echo "⚠️  Target not found for symlink: $symlink -> $target"
    fi
done

echo "✅ Symlinks replaced with actual files"