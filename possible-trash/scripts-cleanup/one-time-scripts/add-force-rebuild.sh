#!/usr/bin/env bash
set -euo pipefail

MF="${1:-Makefile}"
[[ -f "$MF" ]] || { echo "Makefile not found: $MF"; exit 1; }

# Targets we want to force-rebuild-able
targets='^(\$\(POSTMAN_API_UID_FILE\)|\$\(POSTMAN_COLLECTION_RAW\)|\$\(POSTMAN_COLLECTION_UID_FILE\)|\$\(POSTMAN_LINK_STAMP\)|\$\(POSTMAN_TEST_COLLECTION_WITH_EXAMPLES\)|\$\(POSTMAN_TEST_COLLECTION_MERGED\)|\$\(POSTMAN_TEST_COLLECTION_WITH_TESTS\)|\$\(POSTMAN_TEST_COLLECTION_FIXED\)|\$\(POSTMAN_TEST_COLLECTION_UID_FILE\)|\$\(POSTMAN_ENV_UID_FILE\)|\$\(POSTMAN_MOCK_URL_FILE\) \$\(POSTMAN_MOCK_UID_FILE\)|\$\(REDOC_HTML_OUTPUT\) \$\(OPENAPI_BUNDLED_FILE\)|\$\(OPENAPI_LINT_STAMP\)|\$\(C2MAPIV2_OPENAPI_SPEC\)):' 

tmp="${MF}.new"
bak="${MF}.bak.$(date +%Y%m%d-%H%M%S)"

awk -v T="$targets" '
  $0 ~ T {
    # already has FORCE / FORCE_REBUILD?
    if ($0 ~ /\|\s*\$\((FORCE|FORCE_REBUILD)\)/) { print; next }

    # if line already has a pipe, append to the end (still order-only section)
    if ($0 ~ /\|/) { print $0 " $(FORCE_REBUILD)"; next }

    # otherwise start an order-only section with FORCE_REBUILD
    print $0 " | $(FORCE_REBUILD)"; next
  }
  { print }
' "$MF" > "$tmp"

cp -i "$MF" "$bak"
mv "$tmp" "$MF"

echo "Updated $MF (backup at $bak)"

