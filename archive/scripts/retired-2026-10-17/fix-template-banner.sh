#!/bin/bash

# Fix Template Banner Script
# Use this if the template banner disappears from the documentation

# I5: Respect DOCS_PORT from environment (matches Makefile DOCS_PORT ?= 8080)
DOCS_PORT="${DOCS_PORT:-8080}"

echo "🔧 Fixing Template Banner Documentation..."

# K7: Use Makefile variable so the filename stays in sync if the API name changes.
SPEC_FILE="${C2MAPIV2_OPENAPI_SPEC:-openapi/c2mapiv2-openapi-spec-final.yaml}"

# Step 1: Check if OpenAPI spec has JWT overlay (which breaks the banner)
if grep -q "Auth Overlay" "$SPEC_FILE"; then
    echo "⚠️  Found JWT overlay in OpenAPI spec. Reverting to original..."
    git checkout HEAD -- "$SPEC_FILE"
    echo "✅ Reverted OpenAPI spec to original"
fi

# Step 2: Rebuild documentation
echo "🏗️  Rebuilding documentation..."
make docs-build

# Step 3: Restart documentation server
echo "🔄 Restarting documentation server..."
# Kill any existing server
pkill -f "python3 -m http.server ${DOCS_PORT}" 2>/dev/null || true
sleep 2

# Start new server
make docs-serve-bg

echo "✅ Template banner fix complete!"
echo ""
echo "🌐 Documentation should now be available at http://localhost:${DOCS_PORT}"
echo "💡 Try these if banner still doesn't appear:"
echo "   - Hard refresh browser (Cmd+Shift+R)"
echo "   - Open in incognito/private window"
echo "   - Clear browser cache"